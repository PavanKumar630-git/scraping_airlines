# import warnings
# warnings.filterwarnings("ignore")

# import requests
# from scripts.lufhansa.lufhansa import cookies


# class LufthansaService:

#     TOKEN_URL = "https://api-shop.lufthansa.com/v1/oauth2/token"
#     BASE_URL = "https://api-shop.lufthansa.com/v1/one-booking/purchase/orders"

#     CLIENT_ID = "k7zpj4s6k2qbrr4xhrzqa7yn"
#     CLIENT_SECRET = "rVXq#05"
    

#     # ======================================================
#     # GET TOKEN
#     # ======================================================
#     @staticmethod
#     def get_token():
#         headers = {
#             'accept': 'application/json',
#             'accept-language': 'en-US,en;q=0.9',
#             'callid': 'bbd0f537-d60a-47be-ac1c-7d9fe29ef215',
#             'content-type': 'application/x-www-form-urlencoded',
#             'origin': 'https://shop.lufthansa.com',
#             'priority': 'u=1, i',
#             'referer': 'https://shop.lufthansa.com/',
#             'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
#             'sec-ch-ua-mobile': '?0',
#             'sec-ch-ua-platform': '"Windows"',
#             'sec-fetch-dest': 'empty',
#             'sec-fetch-mode': 'cors',
#             'sec-fetch-site': 'same-site',
#             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
#         }

#         data = {
#             'client_id': 'k7zpj4s6k2qbrr4xhrzqa7yn',
#             'client_secret': 'rVXq#05',
#             'fact': '{"keyValuePairs":[{"key":"country","value":"IN"}]}',
#             'grant_type': 'client_credentials',
#         }

#         response = requests.post('https://api-shop.lufthansa.com/v1/oauth2/token', headers=headers, data=data)

#         try:

#             cookies = response.json()
#             token = cookies['access_token']

#             return token  # Return None if the cookie key isn't found
#         except Exception as ee:
#             print("error in token getting:",ee)
#             return None
    
#     # ======================================================
#     # FETCH BOOKING
#     # ======================================================
#     @staticmethod
#     def fetch_booking(pnr, last_name):

#         token = LufthansaService.get_token()
#         print("Token>>>>>>>>>>>>>>",token)
        
#         if not token:
#             return {
#                 "status": "error",
#                 "message": "Unable to generate access token"
#             }

#         # headers = {
#         #     "accept": "application/json",
#         #     "authorization": f"Bearer {token}",
#         #     "content-type": "application/json",
#         #     "origin": "https://shop.lufthansa.com",
#         #     "referer": "https://shop.lufthansa.com/",
#         #     "user-agent": "Mozilla/5.0"
#         # }

#         headers = {
#         'accept': 'application/json',
#         'accept-language': 'en-US,en;q=0.9',
#         'ama-client-ref': 'bbd0f537-d60a-47be-ac1c-7d9fe29ef215:1',
#         'authorization': 'Bearer '+str(token),
#         'cache-control': 'max-age=0',
#         'callid': 'bbd0f537-d60a-47be-ac1c-7d9fe29ef215:1',
#         'content-type': 'application/json',
#         'origin': 'https://shop.lufthansa.com',
#         'priority': 'u=1, i',
#         'referer': 'https://shop.lufthansa.com/',
#         'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
#         'sec-ch-ua-mobile': '?0',
#         'sec-ch-ua-platform': '"Windows"',
#         'sec-fetch-dest': 'empty',
#         'sec-fetch-mode': 'cors',
#         'sec-fetch-site': 'same-site',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
#     }
#         print("Headers >>>>>>>>>>>>>>>>>>",headers)
#         # api_url = f"{LufthansaService.BASE_URL}/{pnr}?lastName={last_name}&showOrderEligibilities=true"
#         api_url = f"https://api-shop.lufthansa.com/v1/one-booking/purchase/orders/{pnr}?lastName={last_name}&showOrderEligibilities=true"

#         print(api_url)
#         try:

#             response = requests.get(
#                 api_url,
#                 headers=headers,
#                 verify=False
#             )

#             data = response.json()
#             print(data)
#             # check error
#             if data.get("errors") or data.get("error"):

#                 return {
#                     "status": "error",
#                     "message": "Booking not found",
#                     "data": data
#                 }

#             return {
#                 "status": "success",
#                 "data": data
#             }

#         except Exception as e:

#             return {
#                 "status": "error",
#                 "message": str(e)
#             }

import warnings
warnings.filterwarnings("ignore")

import json
import time

from curl_cffi import requests
from DrissionPage import ChromiumPage, ChromiumOptions


class LufthansaService:

    TOKEN_URL = "https://api-shop.lufthansa.com/v1/oauth2/token"
    BASE_URL = "https://api-shop.lufthansa.com/v1/one-booking/purchase/orders"

    CLIENT_ID = "k7zpj4s6k2qbrr4xhrzqa7yn"
    CLIENT_SECRET = "rVXq#05"

    # ======================================================
    # GENERATE COOKIES USING DRISSION BROWSER
    # ======================================================
    @staticmethod
    def generate_cookies():

        try:

            co = ChromiumOptions()
            co.set_argument("--headless=new")

            page = ChromiumPage(co)

            page.get("https://www.lufthansa.com/de/en/my-bookings")

            time.sleep(12)

            cookie_list = page.cookies()

            cookies = {c["name"]: c["value"] for c in cookie_list}

            page.quit()

            print("Generated Cookies >>>", cookies)

            return cookies

        except Exception as e:
            print("Cookie generation error:", e)
            return {}

    # ======================================================
    # GET TOKEN
    # ======================================================
    @staticmethod
    def get_token(session, cookies):

        headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://www.lufthansa.com",
            "referer": "https://www.lufthansa.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
        }

        data = {
            "client_id": LufthansaService.CLIENT_ID,
            "client_secret": LufthansaService.CLIENT_SECRET,
            "fact": '{"keyValuePairs":[{"key":"country","value":"IN"}]}',
            "grant_type": "client_credentials",
        }

        try:

            response = session.post(
                LufthansaService.TOKEN_URL,
                headers=headers,
                data=data,
                cookies=cookies,
                impersonate="chrome124"
            )

            print("TOKEN STATUS >>>", response.status_code)
            print("TOKEN RESPONSE >>>", response.text)

            if response.status_code != 200:
                return None

            token = response.json().get("access_token")

            return token

        except Exception as e:
            print("Token error:", e)
            return None

    # ======================================================
    # FETCH BOOKING
    # ======================================================
    @staticmethod
    def fetch_booking(pnr, last_name):

        try:

            # STEP 1: Browser cookies
            cookies = LufthansaService.generate_cookies()

            if not cookies:
                return {
                    "status": "error",
                    "message": "Unable to generate cookies"
                }

            # STEP 2: Same session for token + API
            session = requests.Session()

            # STEP 3: Token
            token = LufthansaService.get_token(session, cookies)

            print("Access Token >>>", token)

            if not token:
                return {
                    "status": "error",
                    "message": "Unable to generate access token"
                }

            # STEP 4: Booking request headers
            headers = {
                "accept": "application/json",
                "authorization": f"Bearer {token}",
                "origin": "https://www.lufthansa.com",
                "referer": "https://www.lufthansa.com/",
                "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
            }

            api_url = f"{LufthansaService.BASE_URL}/{pnr}?lastName={last_name}&showOrderEligibilities=true"

            print("API URL >>>", api_url)

            response = session.get(
                api_url,
                headers=headers,
                cookies=cookies,
                impersonate="chrome124"
            )

            print("BOOKING STATUS >>>", response.status_code)
            print("BOOKING RESPONSE >>>", response.text)

            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": "Access blocked",
                    "data": response.text
                }

            data = response.json()

            return {
                "status": "success",
                "data": data
            }

        except Exception as e:

            return {
                "status": "error",
                "message": str(e)
            }