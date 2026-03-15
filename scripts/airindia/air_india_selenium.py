# #============================
# from playwright.sync_api import sync_playwright
# from curl_cffi import requests
# import json

# def get_incap_tokens(pnr: str, last_name: str):
#     with sync_playwright() as p:

#         browser = p.chromium.launch(
#         headless=True,
#         channel="msedge",
#         args=[
#             "--disable-blink-features=AutomationControlled",
#             "--disable-http2",                          # fixes ERR_HTTP2_PROTOCOL_ERROR
#             "--no-sandbox",
#             "--disable-dev-shm-usage",
#             "--disable-gpu",
#             "--window-size=1920,1080",
#             "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
#             ]
#         )
#         context = browser.new_context(
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
#             viewport={"width": 1920, "height": 1080},
#             locale="en-US",
#             timezone_id="Asia/Kolkata",
#             # Make headless look like a real browser
#             extra_http_headers={
#                 "Accept-Language": "en-US,en;q=0.9",
#             }
#         )
#         page = context.new_page()

#         # Patch multiple headless detection points
#         page.add_init_script("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
#             Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
#             window.chrome = { runtime: {} };
#         """)

#         # browser = p.chromium.launch(
#         #     headless=True,
#         #     args=["--disable-blink-features=AutomationControlled"]
#         # )
#         # context = browser.new_context(
#         #     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
#         #     viewport={"width": 1920, "height": 1080},
#         # )
#         # page = context.new_page()
#         # page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

#         page.goto("https://www.airindia.com/in/en/manage/booking.html", wait_until="domcontentloaded", timeout=60000)
#         page.wait_for_selector("#pnr-ip-id", timeout=30000)

#         try:
#             page.click("#onetrust-accept-btn-handler", timeout=5000)
#         except:
#             print("No cookie banner found, continuing...")

#         page.fill("#pnr-ip-id", pnr)
#         page.fill("#lastname-ip-id", last_name)
#         page.click("xpath=//*[@id='managebookingangular']/div/form/div[4]/button")

#         print("Waiting for tokens...")
#         page.wait_for_function("window.localStorage.getItem('reese84') !== null", timeout=30000)
#         page.wait_for_function("window.localStorage.getItem('x-incap-spa-info') !== null", timeout=30000)

#         reese84 = page.evaluate("window.localStorage.getItem('reese84')")
#         incap   = page.evaluate("window.localStorage.getItem('x-incap-spa-info')")
#         cookies = context.cookies()
#         browser.close()

#         return {
#             "reese84": reese84,
#             "x-incap-spa-info": incap,
#             "cookies": cookies
#         }


# def construct_headers_and_cookies(tokens: dict) -> tuple:
#     reese84_data = json.loads(tokens["reese84"])
#     x_d_token = reese84_data["token"]

#     incap_data = json.loads(tokens["x-incap-spa-info"])
#     travel_cookies = incap_data.get("https://travel.airindia.com", [])
#     incap_cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in travel_cookies)

#     base_headers = {
#         'accept': 'application/json',
#         'accept-language': 'en-US,en;q=0.9',
#         'origin': 'https://travel.airindia.com',
#         'referer': 'https://travel.airindia.com/',
#         'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
#         'sec-ch-ua-mobile': '?0',
#         'sec-ch-ua-platform': '"Windows"',
#         'sec-fetch-dest': 'empty',
#         'sec-fetch-mode': 'cors',
#         'sec-fetch-site': 'same-site',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
#         'x-d-token': x_d_token,
#         'x-incap-spa-info': incap_cookie_str,
#         'x-spa': '1',
#     }

#     cookies = {}
#     for c in tokens["cookies"]:
#         if "airindia.com" in c.get("domain", ""):
#             cookies[c["name"]] = c["value"]
#     cookies["reese84"] = x_d_token

#     return base_headers, cookies


# def get_bearer_token(session: requests.Session, base_headers: dict, cookies: dict) -> str:
#     print("Getting Bearer token...")

#     token_headers = {**base_headers, 'content-type': 'application/x-www-form-urlencoded'}

#     data = {
#         'client_id': 'DCkj8EM4xxOUnINtcYcUhGXVfP2KKUzf',
#         'client_secret': 'QWgBtA2ARMfdAf1g',
#         'grant_type': 'client_credentials',
#         'guest_office_id': 'DELAI08AA',
#     }

#     response = session.post(
#         'https://api-des.airindia.com/v1/security/oauth2/token',
#         headers=token_headers,
#         cookies=cookies,
#         data=data,
#         impersonate="chrome124"
#     )

#     print(f"Token status: {response.status_code}")
#     result = response.json()
#     print(f"Token response: {result}")

#     access_token = result.get("access_token")
#     if not access_token:
#         raise Exception(f"Failed to get access token: {result}")

#     print(f"Bearer token: {access_token[:30]}...")
#     return access_token


# def fetch_booking(pnr: str, last_name: str):
#     # Step 1: Get tokens via browser
#     tokens = get_incap_tokens(pnr, last_name)
#     base_headers, cookies = construct_headers_and_cookies(tokens)

#     session = requests.Session()

#     # Step 2: Get Bearer token
#     bearer_token = get_bearer_token(session, base_headers, cookies)

#     # Step 3: Hit booking API with Bearer token
#     booking_headers = {
#         **base_headers,
#         'authorization': f'Bearer {bearer_token}',
#         'content-type': 'application/json',
#     }

#     params = {
#         'lastName': last_name,
#         'showOrderEligibilities': 'true',
#         'checkServicesAndSeatsIssuanceCurrency': 'false',
#     }

#     print(f"\nFetching booking {pnr}...")
#     response = session.get(
#         f'https://api-des.airindia.com/v2/purchase/orders/{pnr}',
#         params=params,
#         headers=booking_headers,
#         cookies=cookies,
#         impersonate="chrome124"
#     )

#     print(f"Booking status: {response.status_code}")

#     if response.status_code == 200:
#         return response.json()
#     else:
#         print("Error response:", response.text[:500])
#         return None


# result = fetch_booking('98RZ64', 'PUROHIT')
# print(json.dumps(result, indent=2))






from playwright.sync_api import sync_playwright
from curl_cffi import requests
import json

def get_incap_tokens(pnr: str, last_name: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-http2",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1920,1080",
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="Asia/Kolkata",
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"}
        )
        page = context.new_page()
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            window.chrome = { runtime: {} };
        """)

        page.goto("https://www.airindia.com/in/en/manage/booking.html", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("#pnr-ip-id", timeout=30000)

        try:
            page.click("#onetrust-accept-btn-handler", timeout=5000)
        except:
            print("No cookie banner found, continuing...")

        page.fill("#pnr-ip-id", pnr)
        page.fill("#lastname-ip-id", last_name)
        page.click("xpath=//*[@id='managebookingangular']/div/form/div[4]/button")

        print("Waiting for tokens...")

        # Wait for reese84 first
        page.wait_for_function("window.localStorage.getItem('reese84') !== null", timeout=30000)
        print("reese84 found!")

        # x-incap-spa-info is set on travel.airindia.com after redirect
        # Wait for page navigation first
        print(f"Current URL: {page.url}")
        print("Waiting for redirect to travel.airindia.com...")

        # Wait up to 60s for the redirect and token
        try:
            page.wait_for_url("**/travel.airindia.com/**", timeout=60000)
            print(f"Redirected to: {page.url}")
        except:
            print(f"No redirect, still at: {page.url}")

        # Now wait for x-incap-spa-info with longer timeout
        try:
            page.wait_for_function(
                "window.localStorage.getItem('x-incap-spa-info') !== null",
                timeout=60000
            )
            print("x-incap-spa-info found!")
        except:
            # Debug: dump all localStorage
            all_storage = page.evaluate("""
                () => {
                    let items = {};
                    for (let i = 0; i < localStorage.length; i++) {
                        let key = localStorage.key(i);
                        items[key] = localStorage.getItem(key);
                    }
                    return items;
                }
            """)
            print(f"localStorage keys found: {list(all_storage.keys())}")

            # x-incap-spa-info might be on the original domain's localStorage
            # Try getting it from www.airindia.com context
            incap_val = all_storage.get("x-incap-spa-info")
            if incap_val:
                print("Found x-incap-spa-info in current page localStorage!")
            else:
                # It may be stored on the parent domain - navigate back and check
                print("x-incap-spa-info not found in localStorage, checking cookies for incap values...")
                all_cookies = context.cookies()
                incap_cookies = [c for c in all_cookies if "incap" in c["name"].lower() or "nlbi" in c["name"].lower()]
                print(f"Incap cookies: {incap_cookies}")

        reese84 = page.evaluate("window.localStorage.getItem('reese84')")
        incap   = page.evaluate("window.localStorage.getItem('x-incap-spa-info')")
        cookies = context.cookies()

        print(f"\nreese84: {'found' if reese84 else 'MISSING'}")
        print(f"x-incap-spa-info: {'found' if incap else 'MISSING'}")

        browser.close()

        return {
            "reese84": reese84,
            "x-incap-spa-info": incap,
            "cookies": cookies
        }


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
        if "airindia.com" in c.get("domain", ""):
            cookies[c["name"]] = c["value"]
    cookies["reese84"] = x_d_token

    return base_headers, cookies


def get_bearer_token(session: requests.Session, base_headers: dict, cookies: dict) -> str:
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
        raise Exception(f"Failed to get access token: {result}")
    print(f"Bearer token obtained: {access_token[:20]}...")
    return access_token


def fetch_booking(pnr: str, last_name: str):
    tokens = get_incap_tokens(pnr, last_name)
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
        print("Error response:", response.text[:500])
        return None


result = fetch_booking('98RZ64', 'PUROHIT')
print(json.dumps(result, indent=2))