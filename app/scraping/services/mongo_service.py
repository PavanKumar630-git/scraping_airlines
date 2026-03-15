
# from pymongo import MongoClient
# import datetime

# class MongoService:

#     def __init__(self):
#         # self.client = MongoClient("mongodb://localhost:27017")
#         # self.db = self.client["scraper_db"]
#         print("mongo")

#     def get_collection(self, name):
#         return self.db[name]

#     def insert_or_update(self, collection, query, data):
#         data["updated_at"] = datetime.datetime.utcnow()
#         collection.update_one(query, {"$set": data}, upsert=True)

#     def get_all(self, collection):
#         return list(collection.find({}, {"_id": 0}))


from pymongo import MongoClient
import datetime


class MongoService:

    def __init__(self):

        MONGO_URI = "mongodb+srv://scraping:scraping@scraping.w3hsqwj.mongodb.net/"
        DB_NAME = "airlines_db"

        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]

    def get_collection(self, name):
        return self.db[name]

    def insert_one(self, collection_name, data):
        collection = self.get_collection(collection_name)

        data["created_at"] = datetime.datetime.utcnow()

        collection.insert_one(data)

    def insert_many(self, collection_name, data_list):
        collection = self.get_collection(collection_name)

        for item in data_list:
            item["created_at"] = datetime.datetime.utcnow()

        collection.insert_many(data_list)

    def insert_or_update(self, collection_name, query, data):
        collection = self.get_collection(collection_name)

        data["updated_at"] = datetime.datetime.utcnow()

        collection.update_one(
            query,
            {"$set": data},
            upsert=True
        )

    def get_all(self, collection_name):
        collection = self.get_collection(collection_name)

        return list(collection.find({}, {"_id": 0}))
    
    
    def check_pnr_exists(self, collection_name: str, query: dict) -> dict:
        collection = self.get_collection(collection_name)
        doc = collection.find_one(query, {"ci_id": 1, "_id": 0})
        return {"exists": bool(doc), "ci_id": doc.get("ci_id") if doc else None}

    def soft_delete(self, pnr: str, ci_id: str) -> dict:
        raw_result = self.get_collection("airlines_raw_data").update_one(
            {"pnr": pnr, "ci_id": ci_id},
            {"$set": {"is_deleted": True, "deleted_at": datetime.datetime.utcnow()}}
        )

        if raw_result.matched_count == 0:
            return {"success": False, "message": f"No record found for PNR {pnr} and ci_id {ci_id}"}

        collections = ["header_info", "pax_info", "flight_info", "fare_info"]
        updated_counts = {}

        for col_name in collections:
            result = self.get_collection(col_name).update_many(
                {"parent_ci_id": ci_id},
                {"$set": {"is_deleted": True, "deleted_at": datetime.datetime.utcnow()}}
            )
            updated_counts[col_name] = result.modified_count

        return {
            "success": True,
            "message": f"Soft deleted PNR {pnr} with ci_id {ci_id}",
            "modified": {
                "airlines_raw_data": raw_result.modified_count,
                **updated_counts
            }
        }