# mongodb.py
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['User_Database']
collection = db['Users']
