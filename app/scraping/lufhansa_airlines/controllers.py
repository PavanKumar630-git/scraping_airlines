
import requests
from bs4 import BeautifulSoup
from .services import LufthansaService
from app.scraping.services.mongo_service import MongoService
from app.scraping.services.pdf_service import PDFService
from airlines_main.utility import *
from app.scraping.lufhansa_airlines.lufhansa_service import *

class LufhansaController:
    
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
            result = LufthansaService.fetch_booking(pnr, last_name)

            # Step 2: Generate CI ID
            # ci_id = generate_numeric_uuid()

            # # Step 3: Ingest data into MongoDB
            # ingestion = BookingIngestionService(result, ci_id)
            # ingestion_result = ingestion.ingest()

            return {
                "status": "success",
                "message": "Booking stored successfully",
                "data": result
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
        