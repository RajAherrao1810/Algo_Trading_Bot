from fastapi import FastAPI, Request
from pymongo import MongoClient
from fastapi.responses import HTMLResponse

app=FastAPI()

conn=MongoClient("mongodb://localhost:27017/")
user_db = conn["User_Database"]
Live_positions=conn["Live_Data_Feed"]

@app.get("/ltp")
async def get_ltp(index:str):
    item = Live_positions["Live_feed"].find_one({"Symbol": index})
    if item:
        return item["LTP"]
    return {"message": "Item not found"}

@app.get("/user_verification")
async def verify_user(email:str):
    item = user_db["Users"].find_one({"email": email})
    if item:
        return item["password"]
    return {"message": "Item not found"}

@app.post("/items/")
async def create_item(item: dict):
    result = await Live_positions["Live_feed"].insert_one(item)
    return {"inserted_id": str(result.inserted_id)}
