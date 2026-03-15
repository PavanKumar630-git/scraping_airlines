import os
import json
import uuid
from pymongo import MongoClient

# MongoDB configuration
MONGO_URI = "mongodb+srv://scraping:scraping@scraping.w3hsqwj.mongodb.net/"
DB_NAME = "insurance_db"

# Folder containing JSON files
JSON_FOLDER = "json_files"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

insurance_companies = db["insurance_companies"]
insurance_data = db["insurance_data"]

# Create indexes
insurance_companies.create_index("ci_id", unique=True)
insurance_companies.create_index("company_name", unique=True)
insurance_data.create_index("ci_id")


# Generate numeric UUID stored as STRING
def generate_numeric_uuid():
    return str(uuid.uuid4().int % 10**18)


# Process JSON files
for file in os.listdir(JSON_FOLDER):

    if file.endswith(".json"):

        company_name = os.path.splitext(file)[0].lower()

        # Check if company already exists
        company = insurance_companies.find_one({"company_name": company_name})

        if company:
            ci_id = str(company["ci_id"])
            print(f"{company_name} already exists with ci_id {ci_id}")

        else:
            ci_id = generate_numeric_uuid()

            insurance_companies.insert_one({
                "ci_id": ci_id,
                "company_id": company_name,
                "company_name": company_name,
                "company_type": "insurance"
            })

            print(f"Created company {company_name} with ci_id {ci_id}")

        # Read JSON file
        file_path = os.path.join(JSON_FOLDER, file)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        records = []

        if isinstance(data, list):

            for row in data:
                row["ci_id"] = ci_id
                row["company"] = company_name
                records.append(row)

        else:
            data["ci_id"] = ci_id
            data["company"] = company_name
            records.append(data)

        # Insert records
        if records:
            insurance_data.insert_many(records)

        print(f"{len(records)} records inserted for {company_name}")

print("All JSON files processed successfully")