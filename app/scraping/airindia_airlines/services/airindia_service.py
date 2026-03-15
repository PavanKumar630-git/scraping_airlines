from curl_cffi import requests
import json
from DrissionPage import ChromiumPage, ChromiumOptions

from airlines_main.utility import generate_numeric_uuid


class AirIndiaService:

    @staticmethod
    def get_tokens_drission(pnr: str, last_name: str):
        opts = ChromiumOptions()
        opts.auto_port()
        opts.headless(False)
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
            page.wait.doc_loaded()
            page.wait(3)

            try:
                page.ele("#onetrust-accept-btn-handler", timeout=8).click()
                page.wait(1)
            except:
                pass

            pnr_el = page.ele("#pnr-ip-id", timeout=20)
            pnr_el.clear()
            pnr_el.input(pnr)

            lname_el = page.ele("#lastname-ip-id", timeout=10)
            lname_el.clear()
            lname_el.input(last_name)

            submit = page.ele('xpath://*[@id="managebookingangular"]/div/form/div[4]/button', timeout=10)
            submit.click()
            print("Sumited the PNR and Last Name......................")
            page.wait(8)

            reese84 = None
            for i in range(30):
                reese84 = page.run_js("return window.localStorage.getItem('reese84')")
                if reese84:
                    break
                page.wait(1)
            if not reese84:
                raise Exception("reese84 not found after 30s")

            incap = None
            for i in range(60):
                incap = page.run_js("return window.localStorage.getItem('x-incap-spa-info')")
                if incap:
                    break
                page.wait(1)
            if not incap:
                raise Exception("x-incap-spa-info not found after 60s")

            cookies = page.cookies()
            return {
                "reese84": reese84,
                "x-incap-spa-info": incap,
                "cookies": [{"name": c["name"], "value": c["value"], "domain": c.get("domain", "")} for c in cookies]
            }
        finally:
            page.quit()

    @staticmethod
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

    @staticmethod
    def get_bearer_token(session, base_headers: dict, cookies: dict) -> str:
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
        result = response.json()
        access_token = result.get("access_token")
        if not access_token:
            raise Exception(f"Failed to get Bearer token: {result}")
        return access_token

    @staticmethod
    def fetch_booking(pnr: str, last_name: str) -> dict:
        tokens = AirIndiaService.get_tokens_drission(pnr, last_name)
        print("Got the tokens.............",tokens)
        base_headers, cookies = AirIndiaService.construct_headers_and_cookies(tokens)
        print("Got the base headers and cookies...............",base_headers,cookies)
        session = requests.Session()
        bearer_token = AirIndiaService.get_bearer_token(session, base_headers, cookies)
        print("Got the bearer token...............",bearer_token)
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

        response = session.get(
            f'https://api-des.airindia.com/v2/purchase/orders/{pnr}',
            params=params,
            headers=booking_headers,
            cookies=cookies,
            impersonate="chrome124"
        )
        print("Got the final response...............",response.status_code)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Booking fetch failed [{response.status_code}]: {response.text[:300]}")


# Usage:
# if __name__ == "__main__":
#     result = AirIndiaService.fetch_booking('98RZ64', 'PUROHIT')
#     print(json.dumps(result, indent=2))
 
############################################################################################################################
        
import uuid
from datetime import datetime

from app.scraping.services.mongo_service import MongoService

from datetime import datetime


class BookingIngestionService:

    def __init__(self, raw_data, ci_id):

        self.raw = raw_data
        self.data = raw_data.get("data", raw_data)
        self.ci_id = str(ci_id)

        mongo = MongoService()

        self.raw_col = mongo.get_collection("airlines_raw_data")
        self.header_col = mongo.get_collection("header_info")
        self.pax_col = mongo.get_collection("pax_info")
        self.flight_col = mongo.get_collection("flight_info")
        self.fare_col = mongo.get_collection("fare_info")

    # =========================================================
    # MAIN INGEST
    # =========================================================

    def ingest(self):

        pnr = self.data.get("id")
        last_name = self._extract_last_name()

        self._store_raw_data(pnr, last_name)

        header_doc = self._build_header(pnr, last_name)
        pax_docs = self._build_pax(pnr, last_name)
        flight_docs = self._build_flight(pnr, last_name)
        fare_docs = self._build_fare(pnr, last_name)

        header_id = self.header_col.insert_one(header_doc).inserted_id

        pax_ids = [self.pax_col.insert_one(p).inserted_id for p in pax_docs]
        flight_ids = [self.flight_col.insert_one(f).inserted_id for f in flight_docs]
        fare_ids = [self.fare_col.insert_one(f).inserted_id for f in fare_docs]

        return {
            "ci_id": self.ci_id,
            "pnr": pnr,
            "last_name": last_name,
            "inserted_ids": {
                "header": str(header_id),
                "pax": [str(i) for i in pax_ids],
                "flight": [str(i) for i in flight_ids],
                "fare": [str(i) for i in fare_ids],
            },
        }

    # =========================================================
    # RAW DATA
    # =========================================================

    def _store_raw_data(self, pnr, last_name):

        self.raw_col.insert_one({
            "ci_id": self.ci_id,
            "pnr": pnr,
            "last_name": last_name,
            "airline": "Air India",
            "raw_data": self.raw,
            "created_at": datetime.utcnow()
        })

    # =========================================================
    # HEADER
    # =========================================================

    def _build_header(self, pnr, last_name):

        travel_docs = self.data.get("travelDocuments", [])
        ticket = travel_docs[0] if travel_docs else {}
        each_ci_id = generate_numeric_uuid()
        return {
            "parent_ci_id": self.ci_id,
            "ci_id":each_ci_id,
            "pnr": pnr,
            "last_name": last_name,
            "airline": "Air India",

            "order_id": self.data.get("id"),
            "creation_datetime": self.data.get("creationDateTime"),
            "last_modification_datetime": self.data.get("lastModificationDateTime"),

            "creation_pos": self.data.get("creationPointOfSale"),
            "servicing_pos": self.data.get("servicingPointOfSale"),

            "is_group_booking": self.data.get("isGroupBooking", False),

            "ticket_number": ticket.get("id"),   # FIXED
            "document_type": ticket.get("documentType"),
            "status": ticket.get("status"),

            "endorsement": ticket.get("endorsement"),
            "tour_code": ticket.get("tourCode"),

            "issuance_office": ticket.get("issuanceOffice"),
            "issuance_city": ticket.get("issuanceCity"),
            "issuance_date": ticket.get("issuanceDate"),

            "contacts": self.data.get("contacts", []),
            "remarks": self.data.get("remarks", []),

            "warnings": self.raw.get("warnings", []),
            "order_eligibilities": self.data.get("orderEligibilities"),

            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

    # =========================================================
    # PASSENGERS
    # =========================================================

    def _build_pax(self, pnr, last_name):

        pax_docs = []

        travelers = self.data.get("travelers", [])
        seats = self.data.get("seats", [])
        services = self.data.get("services", [])

        for traveler in travelers:

            name = traveler.get("names", [{}])[0]
            traveler_id = traveler.get("id")

            # Map seats for this traveler
            mapped_seats = []
            for seat in seats:

                traveler_ids = seat.get("travelerIds") or [seat.get("travelerId")]

                if traveler_id in traveler_ids:
                    mapped_seats.append(seat)

            # Map services for this traveler
            mapped_services = []
            for svc in services:

                traveler_ids = svc.get("travelerIds") or [svc.get("travelerId")]

                if traveler_id in traveler_ids:
                    mapped_services.append(svc)
            each_ci_id = generate_numeric_uuid()
            pax_docs.append({
                "parent_ci_id": self.ci_id,
                "ci_id":each_ci_id,
                "pnr": pnr,
                "last_name": last_name,
                "airline": "Air India",
                "traveler_id": traveler_id,
                "passenger_type_code": traveler.get("passengerTypeCode"),

                "first_name": name.get("firstName"),
                "last_name": name.get("lastName"),
                "title": name.get("title"),

                "regulatory_details": traveler.get("regulatoryDetails", []),

                "seats": mapped_seats,
                "services": mapped_services,

                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            })

        return pax_docs
    # =========================================================
    # FLIGHTS
    # =========================================================

    
    def _build_flight(self, pnr, last_name):
        flights = []

        air = self.data.get("air", {})
        bounds = air.get("bounds", [])

        flight_dict = self.raw.get("dictionaries", {}).get("flight", {})

        for bound in bounds:

            for fl in bound.get("flights", []):

                segment_id = fl.get("id")

                flight_info = flight_dict.get(segment_id, {})
                each_ci_id = generate_numeric_uuid()
                
                flights.append({
                    "parent_ci_id": self.ci_id,
                    "ci_id":each_ci_id,
                    "pnr": pnr,
                    "last_name": last_name,
                    "airline": "Air India",
                    "air_bound_id": bound.get("airBoundId"),

                    "origin": bound.get("originLocationCode"),
                    "destination": bound.get("destinationLocationCode"),

                    "duration": bound.get("duration"),
                    "fare_family_code": bound.get("fareFamilyCode"),

                    "is_disrupted": bound.get("isDisrupted"),
                    "disruption_status": bound.get("disruptionStatus"),

                    "segment_id": segment_id,

                    # FIXED
                    "marketing_airline": flight_info.get("marketingAirlineCode"),
                    "flight_number": flight_info.get("marketingFlightNumber"),

                    "departure": flight_info.get("departure"),
                    "arrival": flight_info.get("arrival"),

                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                })

        return flights
    # =========================================================
    # FARE
    # =========================================================

    def _build_fare(self, pnr, last_name):

        fares = []

        travel_docs = self.data.get("travelDocuments", [])

        for doc in travel_docs:

            price = doc.get("price", {})
            each_ci_id = generate_numeric_uuid()
            fares.append({
                "parent_ci_id": self.ci_id,
                "ci_id":each_ci_id,
                "pnr": pnr,
                "last_name": last_name,
                "airline": "Air India",
                "ticket_number": doc.get("id"),  # FIXED
                "traveler_ids": doc.get("travelerIds", []),

                "document_type": doc.get("documentType"),
                "status": doc.get("status"),

                "flight_ids": doc.get("flightIds", []),

                "pricing": price,

                # FIXED (your main issue)
                "fare_breakdowns": doc.get("fareInfos", []),

                "price_breakdowns": price.get("priceBreakdowns", []),

                "payment_transactions": doc.get("paymentTransactions", []),

                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            })

        return fares

    # =========================================================
    # HELPER
    # =========================================================

    def _extract_last_name(self):

        travelers = self.data.get("travelers", [])

        if not travelers:
            return ""

        names = travelers[0].get("names", [])

        if not names:
            return ""

        return names[0].get("lastName", "")