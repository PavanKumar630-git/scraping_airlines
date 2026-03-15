from playwright.sync_api import sync_playwright
from curl_cffi import requests
import json
import urllib.request

def get_free_proxies():
    """Fetch free proxies from public sources"""
    proxies = []
    try:
        # Free proxy list API
        url = "https://proxylist.geonode.com/api/proxy-list?limit=20&page=1&sort_by=lastChecked&sort_type=desc&protocols=http,https&country=US"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            for proxy in data.get("data", []):
                proxies.append(f"{proxy['ip']}:{proxy['port']}")
    except Exception as e:
        print(f"Failed to fetch proxies: {e}")

    # Fallback hardcoded free proxies (may expire)
    fallback = [
        "103.149.162.195:80",
        "20.111.54.16:8123",
        "51.158.172.165:8761",
        "185.105.102.189:3128",
    ]
    return proxies + fallback


def get_incap_tokens(pnr: str, last_name: str, proxy: str = None):
    with sync_playwright() as p:

        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-http2",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1920,1080",
        ]

        if proxy:
            launch_args.append(f"--proxy-server={proxy}")
            print(f"Using proxy: {proxy}")

        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=launch_args
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

        try:
            page.goto("https://www.airindia.com/in/en/manage/booking.html", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("#pnr-ip-id", timeout=30000)
        except Exception as e:
            browser.close()
            raise Exception(f"Page load failed with proxy {proxy}: {e}")

        try:
            page.click("#onetrust-accept-btn-handler", timeout=5000)
        except:
            pass

        page.fill("#pnr-ip-id", pnr)
        page.fill("#lastname-ip-id", last_name)
        page.click("xpath=//*[@id='managebookingangular']/div/form/div[4]/button")

        print("Waiting for tokens...")
        page.wait_for_function("window.localStorage.getItem('reese84') !== null", timeout=30000)
        print("reese84 ✓")

        try:
            page.wait_for_url("*travel.airindia.com*", timeout=60000)
        except:
            print(f"Still at: {page.url}")

        try:
            page.wait_for_function("window.localStorage.getItem('x-incap-spa-info') !== null", timeout=60000)
            print("x-incap-spa-info ✓")
        except:
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
            print(f"localStorage keys: {list(all_storage.keys())}")
            browser.close()
            raise Exception("x-incap-spa-info not found")

        reese84 = page.evaluate("window.localStorage.getItem('reese84')")
        incap   = page.evaluate("window.localStorage.getItem('x-incap-spa-info')")
        cookies = context.cookies()
        browser.close()

        return {"reese84": reese84, "x-incap-spa-info": incap, "cookies": cookies}


def get_incap_tokens_with_retry(pnr: str, last_name: str):
    """Try without proxy first, then rotate through proxies"""

    # Try without proxy first
    print("Trying without proxy...")
    try:
        return get_incap_tokens(pnr, last_name, proxy=None)
    except Exception as e:
        print(f"No proxy failed: {e}")

    # Try with free proxies
    proxies = get_free_proxies()
    print(f"Fetched {len(proxies)} proxies to try...")

    for i, proxy in enumerate(proxies):
        print(f"\nTrying proxy {i+1}/{len(proxies)}: {proxy}")
        try:
            return get_incap_tokens(pnr, last_name, proxy=f"http://{proxy}")
        except Exception as e:
            print(f"Proxy {proxy} failed: {e}")
            continue

    raise Exception("All proxies exhausted, no tokens obtained")


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
        raise Exception(f"Failed to get Bearer token: {result}")
    print(f"Bearer token: {access_token[:20]}...")
    return access_token


def fetch_booking(pnr: str, last_name: str):
    tokens = get_incap_tokens_with_retry(pnr, last_name)
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