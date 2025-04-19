from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(MONGO_URI)
db = client.trafico_rm
events_collection = db.events