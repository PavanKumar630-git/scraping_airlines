import os
import uuid
import requests
import time


class PDFService:

    DOWNLOAD_DIR = "downloads"

    @staticmethod
    def download_pdf(url, company):

        start_time = time.time()

        company_path = os.path.join(PDFService.DOWNLOAD_DIR, company)
        os.makedirs(company_path, exist_ok=True)
        
        uuidAdd = uuid.uuid4().hex[:6]
        filename = f"{uuidAdd}_{url.split('/')[-1]}"

        relative_path = os.path.join(company_path, filename)

        absolute_path = os.path.abspath(relative_path)

        response = requests.get(url, stream=True)

        if response.status_code != 200:
            return {
                "status": False,
                "url": url,
                "message": "Failed to download PDF"
            }

        with open(relative_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        file_size = os.path.getsize(relative_path)

        end_time = time.time()

        return {
            "status": True,
            "url": url,
            "file_name": filename,
            "relative_path": relative_path.replace("\\", "/"),
            "absolute_path": absolute_path.replace("\\", "/"),
            "file_size_bytes": file_size,
            "download_time_seconds": round(end_time - start_time, 2)
        }