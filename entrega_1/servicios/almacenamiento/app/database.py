from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client.get_database(os.getenv("MONGO_DB", "eventos"))
events_collection = db.get_collection(os.getenv("MONGO_COLLECTION", "intento_1"))