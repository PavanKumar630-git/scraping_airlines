from curl_cffi import requests
import json
from DrissionPage import ChromiumPage, ChromiumOptions
def get_tokens_drission(pnr: str, last_name: str):
    opts = ChromiumOptions()
    opts.auto_port()
    opts.headless(True)
    opts.set_argument("--disable-blink-features=AutomationControlled")
    opts.set_argument("--no-sandbox")
    opts.set_argument("--disable-gpu")
    opts.set_argument("--disable-http2")
    opts.set_argument("--window-size=1920,1080")
    opts.set_argument("--start-maximized")
    opts.set_argument("--disable-dev-shm-usage")
    opts.set_argument("--disable-extensions")
    opts.set_argument("--disable-infobars")
    opts.set_argument("--ignore-certificate-errors")
    # Critical: makes headless look like real Chrome
    opts.set_argument("--headless=new")  # use new headless mode instead of old
    opts.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36")
    page = ChromiumPage(opts)
    try:
        page.get("https://www.airindia.com/in/en/manage/booking.html")
        # Wait for page to fully load
        page.wait.doc_loaded()
        page.wait(3)  # extra wait for JS to render
        print(f"Page title: {page.title}")
        print(f"Current URL: {page.url}")
        # Accept cookies
        try:
            page.ele("#onetrust-accept-btn-handler", timeout=8).click()
            print("Cookie banner accepted")
            page.wait(1)
        except:
            print("No cookie banner")
        # Wait for PNR input
        print("Waiting for PNR input...")
        pnr_el = page.ele("#pnr-ip-id", timeout=20)
        if not pnr_el:
            # Try alternative selectors
            pnr_el = page.ele('xpath://input[@id="pnr-ip-id"]', timeout=10)
        pnr_el.clear()
        pnr_el.input(pnr)
        print(f"PNR entered: {pnr}")
        lname_el = page.ele("#lastname-ip-id", timeout=10)
        lname_el.clear()
        lname_el.input(last_name)
        print(f"Last name entered: {last_name}")
        # Submit
        submit = page.ele('xpath://*[@id="managebookingangular"]/div/form/div[4]/button', timeout=10)
        submit.click()
        print("Form submitted")
        # Wait for redirect + tokens
        print("Waiting for tokens...")
        page.wait(8)
        # Poll for reese84
        for i in range(30):
            reese84 = page.run_js("return window.localStorage.getItem('reese84')")
            if reese84:
                print(f"reese84 found after {i+1}s")
                break
            page.wait(1)
        else:
            # Debug localStorage
            all_keys = page.run_js("""
                var keys = [];
                for(var i=0; i<localStorage.length; i++) keys.push(localStorage.key(i));
                return keys;
            """)
            print(f"localStorage keys: {all_keys}")
            print(f"Current URL: {page.url}")
            raise Exception("reese84 not found after 30s")

        # Poll for x-incap-spa-info
        for i in range(60):
            incap = page.run_js("return window.localStorage.getItem('x-incap-spa-info')")
            if incap:
                print(f"x-incap-spa-info found after {i+1}s")
                break
            page.wait(1)
        else:
            raise Exception("x-incap-spa-info not found after 60s")
        cookies = page.cookies()
        print("All tokens retrieved successfully!")
        return {
            "reese84": reese84,
            "x-incap-spa-info": incap,
            "cookies": [{"name": c["name"], "value": c["value"], "domain": c.get("domain", "")} for c in cookies]
        }
    finally:
        page.quit()


def construct_headers_and_cookies(tokens: dict) -> tuple:
    reese84_data = json.loads(tokens["reese84"])
    x_d_token = reese84_data["token"]

    incap_data = json.loads(tokens["x-incap-spa-info"])
    travel_cookies = incap_data.get("https://travel.airindia.com", [])
    incap_cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in travel_cookies)

    base_headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://travel.airindia.com',
        'referer': 'https://travel.airindia.com/',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        'x-d-token': x_d_token,
        'x-incap-spa-info': incap_cookie_str,
        'x-spa': '1',
    }

    cookies = {}
    for c in tokens["cookies"]:
        domain = c.get("domain", "")
        if "airindia.com" in domain:
            cookies[c["name"]] = c["value"]
    cookies["reese84"] = x_d_token

    return base_headers, cookies


def get_bearer_token(session, base_headers, cookies):
    print("Getting Bearer token...")
    token_headers = {**base_headers, 'content-type': 'application/x-www-form-urlencoded'}
    data = {
        'client_id': 'DCkj8EM4xxOUnINtcYcUhGXVfP2KKUzf',
        'client_secret': 'QWgBtA2ARMfdAf1g',
        'grant_type': 'client_credentials',
        'guest_office_id': 'DELAI08AA',
    }
    response = session.post(
        'https://api-des.airindia.com/v1/security/oauth2/token',
        headers=token_headers,
        cookies=cookies,
        data=data,
        impersonate="chrome124"
    )
    print(f"Token status: {response.status_code}")
    result = response.json()
    access_token = result.get("access_token")
    if not access_token:
        raise Exception(f"Failed: {result}")
    print(f"Bearer: {access_token[:20]}...")
    return access_token


def fetch_booking(pnr: str, last_name: str):
    tokens = get_tokens_drission(pnr, last_name)
    base_headers, cookies = construct_headers_and_cookies(tokens)
    session = requests.Session()

    bearer_token = get_bearer_token(session, base_headers, cookies)

    booking_headers = {
        **base_headers,
        'authorization': f'Bearer {bearer_token}',
        'content-type': 'application/json',
    }
    params = {
        'lastName': last_name,
        'showOrderEligibilities': 'true',
        'checkServicesAndSeatsIssuanceCurrency': 'false',
    }

    print(f"\nFetching booking {pnr}...")
    response = session.get(
        f'https://api-des.airindia.com/v2/purchase/orders/{pnr}',
        params=params,
        headers=booking_headers,
        cookies=cookies,
        impersonate="chrome124"
    )
    print(f"Booking status: {response.status_code}")

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.text[:500])
        return None


result = fetch_booking('98RZ64', 'PUROHIT')
print(json.dumps(result, indent=2))