# mongodb.py
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')

#Defining Databases
masterdb=client['Master_Database']
user_db = client['User_Database']
strategy_db=client['Strategies']
feed_db=client['Live_Data_Feed']

#Defining Connections
masterList=masterdb['Master_List']
users = user_db['Users']
my_strategy=strategy_db['My_Strategies']
deployed_strategies=strategy_db['Deployed_Strategies']
live_feed=feed_db['Live_feed']
live_positions=feed_db['Live_Positions']
order_book=feed_db['Order_book']
strategy_templates=strategy_db['Strategy_Templates']