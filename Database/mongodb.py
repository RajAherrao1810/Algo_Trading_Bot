from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

# Initialize MongoDB
mongodb = MongoDB("mongodb://localhost:27017", "ATB")

# Accessing databases
live_positions_db = mongodb.db["Live_Data_Feed"]
user_db = mongodb.db["User_Database"]
