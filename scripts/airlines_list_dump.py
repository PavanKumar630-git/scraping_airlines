import os
import json
import uuid
from pymongo import MongoClient

# MongoDB configuration
MONGO_URI = "mongodb+srv://scraping:scraping@scraping.w3hsqwj.mongodb.net/"
DB_NAME = "airlines_db"

# Folder containing JSON files
JSON_FOLDER = "json_files"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Single collection
airlines_list = db["airlines_list"]

# Create unique index
airlines_list.create_index("ci_id_airline", unique=True)


# Generate numeric UUID stored as STRING
def generate_numeric_uuid():
    return str(uuid.uuid4().int % 10**18)


# Process JSON files
for file in os.listdir(JSON_FOLDER):

    if file.endswith(".json"):

        file_path = os.path.join(JSON_FOLDER, file)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        records = []

        if isinstance(data, list):

            for row in data:

                record = {
                    "ci_id_airline": generate_numeric_uuid(),
                    "airline_name": row.get("airline_name"),
                    "airline_code": row.get("airline_code"),
                    "pnr": row.get("pnr"),
                    "last_name": row.get("last_name"),
                    "ticket_number": row.get("ticket_number"),
                    "extra_details": row.get("extra_details", "")
                }

                records.append(record)

        else:

            record = {
                "ci_id_airline": generate_numeric_uuid(),
                "airline_name": data.get("airline_name"),
                "airline_code": data.get("airline_code"),
                "pnr": data.get("pnr"),
                "last_name": data.get("last_name"),
                "ticket_number": data.get("ticket_number"),
                "extra_details": data.get("extra_details", "")
            }

            records.append(record)

        if records:
            airlines_list.insert_many(records)

        print(f"{len(records)} records inserted from {file}")

print("All JSON files processed successfully")