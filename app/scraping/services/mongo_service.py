
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