# mongodb.py
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')

#Defining Databases
user_db = client['User_Database']
strategy_db=client['Strategies']

#Defining Connections
users = user_db['Users']
my_strategy=strategy_db['My_Strategies']
deployed_strategies=strategy_db['Deployed_Strategies']

