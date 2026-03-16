
import requests
from bs4 import BeautifulSoup
from app.scraping.services.mongo_service import MongoService
from app.scraping.services.pdf_service import PDFService
from airlines_main.utility import *
from app.scraping.lotpolish_airlines.lotpolish_service import *
from app.scraping.lotpolish_airlines.services import *

class LotPolishController:
    
    @staticmethod
    def get_booking_details(payload):

        pnr = payload.get("pnr")
        last_name = payload.get("last_name")

        if not pnr or not last_name:
            return {
                "status": "error",
                "message": "pnr and last_name required"
            }
        validpnr = validate_pnr(pnr)
        if not validpnr:
            return {
                "status": "error",
                "message": "Invalid PNR format. PNR should be 6 characters, alphanumeric and uppercase."
            }
        try:

            mongo = MongoService()

            # Check by PNR + airline before ingesting
            already_exists = mongo.check_pnr_exists("airlines_raw_data", {
                "pnr": pnr,
                "airline": "LotPolish"
            })

            if already_exists['exists']:
                return_data = {
                "status": "failed",
                "message": f"Booking with this PNR already exists, Please Check the PNR in Mongo DB -> airlines_raw_data collection with ci_id: {already_exists['ci_id']}"
                }
                return return_data
            else:
                pass
            # Step 1: Fetch booking from Air India
            scraper = LotPolishBooking(pnr, last_name)

            result = scraper.get_booking()
            print("Result from scraper:", result)
            if result['errors'] and len(result['errors']) > 0:
                return {
                    "status": "error",
                    "message": result
                }
            # Step 2: Generate CI ID
            ci_id = generate_numeric_uuid()

            # Step 3: Ingest data into MongoDB
            ingestion = LotPolishIngestionService(result, ci_id)

            ingestion_result = ingestion.ingest()

            return {
                "status": "success",
                "message": "Booking stored successfully",
                "data": ingestion_result
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
        