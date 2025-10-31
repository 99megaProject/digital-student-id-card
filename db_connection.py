from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env into os.environ

MONGO_URI = os.getenv("MONGO_URI")
# print(MONGO_URI)

def get_collection(collection_name,db_name='College'):
    client = MongoClient(MONGO_URI)
    db = client[db_name]
    collection = db[collection_name]
    return collection



# get_collection("id_card_design")