
import requests
from bs4 import BeautifulSoup
from app.scraping.airindia_airlines.services.airindia_service import AirIndiaService,BookingIngestionService
from app.scraping.services.mongo_service import MongoService
from app.scraping.services.pdf_service import PDFService
from airlines_main.utility import *

class AirIndiaController:

    @staticmethod
    def scrape():
        url = "https://people.sc.fsu.edu/~jburkardt/data/pdf/pdf.html"
        print("Entering scrape function :", url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        # mongo = MongoService()
        # collection = mongo.get_collection("company_a_docs")

        data = []
        alinks = soup.find_all("a")
        pdflinks = [link for link in alinks if link.get("href") and link.get("href").endswith(".pdf")]

        import pdb; pdb.set_trace()

        for link in pdflinks[0:2]:
            eachlink = link.get("href")
            if eachlink.endswith(".pdf"):
                Pdf_Info = PDFService.download_pdf('https://people.sc.fsu.edu/~jburkardt/data/pdf/'+eachlink, "airindia_airlines")
                data.append(Pdf_Info)
                # collection.insert_one(Pdf_Info)

        return {"status": "scraping completed", "data": data}
            
    @staticmethod
    def user_login(payload):

        username = payload.get("username")
        password = payload.get("password")

        if username == "admin" and password == "admin123":
            return {
                "status": "success",
                "message": "login successful"
            }

        return {
            "status": "error",
            "message": "invalid credentials"
        }
    

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
            result = AirIndiaService.fetch_booking(pnr, last_name)

            # Step 2: Generate CI ID
            ci_id = generate_numeric_uuid()

            # Step 3: Ingest data into MongoDB
            ingestion = BookingIngestionService(result, ci_id)
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
        # try:
        #     # result = AirIndiaService.fetch_booking('98RZ64', 'PUROHIT')
        #     result = AirIndiaService.fetch_booking(pnr, last_name)
        #     # Step 2: Save into MongoDB collections
        #     mongo = MongoService()

        #     ci_id = generate_numeric_uuid
        #     # ingestion = BookingIngestionService(result)
            

        #     # result = ingestion.ingest()

        #     return {
        #         "status": "success",
        #         "message": "Booking stored successfully",
        #         "data": result
        #     }
        #     return {
        #         "status": "success",
        #         "data": result
        #     }

        # except Exception as e:
            
        #     return {
        #         "status": "error",
        #         "message": str(e)
        #     }