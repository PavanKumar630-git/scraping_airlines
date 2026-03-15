
import requests
from bs4 import BeautifulSoup
from app.scraping.services.mongo_service import MongoService
from app.scraping.services.pdf_service import PDFService
from airlines_main.utility import *
from app.scraping.srilanka_airlines.srilanka_service import *
from app.scraping.srilanka_airlines.services import *

class SrilankaController:
    
    @staticmethod
    def get_booking_details(payload):

        pnr = payload.get("pnr")
        last_name = payload.get("last_name")

        if not pnr or not last_name:
            return {
                "status": "error",
                "message": "pnr and last_name required"
            }
        try:

            # Step 1: Fetch booking from Air India
            scraper = SriLankanBooking(pnr, last_name)

            result = scraper.get_booking()
            
            # Step 2: Generate CI ID
            ci_id = generate_numeric_uuid()

            # Step 3: Ingest data into MongoDB
            ingestion = SriLankanIngestionService(result, ci_id)

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
        