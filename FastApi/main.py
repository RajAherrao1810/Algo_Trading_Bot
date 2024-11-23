from fastapi import FastAPI, HTTPException
import functions.webSocket as ws
from passlib.context import CryptContext
import bcrypt 
from bson import ObjectId
import functions.config as config
from fastapi.middleware.cors import CORSMiddleware
from functions.mongodb import users, my_strategy, deployed_strategies, live_positions, order_book, strategy_templates
from models.register_models import UserRegister, LoginUser
from models.strategy_models import Strategy, DeployedStrategy, Order, FindStrategyRequest
from functions.instrument import get_master_list
import threading
from strategyExecution import execute_strategy
from fastapi.responses import JSONResponse
from typing import List


app = FastAPI()
obj, sws=ws.login()
ws.connectFeed(sws)
threading.Thread(target=get_master_list, args=(), daemon=True).start()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

"""def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)"""

@app.post("/register")
async def register(user: UserRegister):
    print("Registering user")
    
    # Check if email already exists in the collection
    existing_user = users.find_one({"email": user.email})
    
    # Debugging: print the email being checked
    print(f"Checking for existing user with email: {user.email}")

    if existing_user:
        print("Email is already registered")  # Print statement before raising the exception
        raise HTTPException(status_code=400, detail="Email is already registered")
    
    print("Adding user")

    hashed_password = hash_password(user.password)
    
    # Store the user with plain text password (not recommended)
    new_user = {"email": user.email, "password": hashed_password}
    
    # Insert the new user into the Users collection
    users.insert_one(new_user)
    print("User added successfully")  # Confirmation that the user was added
    return {"message": "User registered successfully"}



@app.post("/login")
async def login(user: LoginUser):
    # Query the MongoDB `Users` collection
    user_data =  users.find_one({"email": user.email})
    
    # Check if user exists and password matches
    if user_data:
        # Check if password matches
        if bcrypt.checkpw(user.password.encode('utf-8'), user_data['password'].encode('utf-8')):
            print('logging in')
            return {"message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid Password")
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    

#route for creating strategy
@app.post("/create_strategy")
async def create_strategy(strategy: Strategy):
    try:
        # Convert the strategy to a dictionary for MongoDB
        strategy_dict = strategy.model_dump(by_alias=True)
        print(strategy_dict)
        insert_strategy=my_strategy.insert_one(strategy_dict)
        print('creating strategy')
        return {"message": "Strategy created successfully", "id":str(insert_strategy.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving strategy: {e}")
    

#route for adding strategy to my startegy page 
@app.post("/add_strategy")
async def add_strategy(strategy:FindStrategyRequest):
    # Fetch strategy details from the strategy_templates collection based on name
    strategy_details = strategy_templates.find_one({"strategyName": strategy.strategyName, "selectedInstrument":strategy.instrument})

    if not strategy_details:
        raise HTTPException(status_code=404, detail="Strategy template not found")

    # Insert the strategy into my_strategies collection
    result = my_strategy.insert_one(strategy_details)

    if result.inserted_id:
        return {"message": "Strategy added successfully to My Strategies"}
    else:
        raise HTTPException(status_code=500, detail="Error adding strategy to the database")

#route for getting strategy for making my_startegy template    
@app.get("/my_strategies")
async def get_my_strategies():
    try:
        strategies = list(my_strategy.find())
        for strategy in strategies:
            # Convert _id to string for JSON serialization
            strategy["_id"] = str(strategy["_id"])
        return {"strategies": strategies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching strategies: {e}")
 
    
#delete strategy from my_strategies
@app.delete("/delete_strategy")
async def delete_strategy(request: FindStrategyRequest):
    try:
        # Use strategyName and instrument to identify the strategy to delete
        result = my_strategy.delete_one({
            "strategyName": request.strategyName,
            "instrument": request.instrument
        })

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Strategy not found")

        return {"message": "Strategy deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting strategy: {e}")


#route for adding strategy to deployed_strategy collection
@app.post("/deployed_strategies")
async def deploy_strategy(strategy: Strategy):
    # Convert strategyId to an ObjectId if needed
    try:
        strategy_dict = strategy.model_dump(by_alias=True)

        #Sorting the legs such that the buy order comes before sell order 
        buy_legs = [leg for leg in strategy_dict['legs'] if leg['buyOrSell'] == 'Buy']
        sell_legs = [leg for leg in strategy_dict['legs'] if leg['buyOrSell'] == 'Sell']
        strategy_dict['legs'] = buy_legs + sell_legs

        #Executing the strategy
        position_dict={
            'strategy_name': strategy.strategyName,
            'Instrument': strategy.selectedInstrument,
            'status': 'running'
        }
        live_positions.insert_one(position_dict)
        threading.Thread(target=execute_strategy, args=(strategy_dict,obj,sws), daemon=True).start()
        insert_strategy=deployed_strategies.insert_one(strategy_dict)
        return {"message": "Strategy deployed successfully", "id":str(insert_strategy.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error deploying strategy") from e


def transform_strategy(strategy:dict):
    return {
        "strategy_name": strategy.get("strategyName", ""),
        "selected_instrument": strategy.get("Instrument", ""),
        "status": strategy.get("status",""),
        "overall_profit_or_loss": strategy.get("overallProfitOrLoss", 0.0),
    }


#route for getting strategy for making deployed_startegy template
@app.get("/deployed_strategy", response_model=list[DeployedStrategy])
async def get_deployed_strategies():
    strategies = [transform_strategy(strategy) for strategy in live_positions.find()]
    return JSONResponse(content=strategies)


@app.get("/order_book", response_model=List[Order])
def get_orders():
    orders=obj.holding()
    transformed_orders = []
    for order in orders["data"]:
        symbol = order["tradingsymbol"]
        quantity = int(order["quantity"])
        avg_price = float(order["fillprice"])
        current_price = float(order["fillprice"])
        pl = (current_price - avg_price) * quantity  # Calculating P/L
        
        transformed_orders.append(
            {
                "symbol": symbol,
                "quantity": quantity,
                "avgPrice": avg_price,
                "currentPrice": current_price,
                "pl": pl,
            }
        )

    order_book.insert_many(transformed_orders)
    orders = list(order_book.find({}, {"_id": 0})) 
    return orders


@app.get("/strategy_templates")
async def get_strategy_templates():
    templates = strategy_templates.find()
    return [
        {"name": template["strategyName"], "Instrument":template["selectedInstrument"],"strategyType":template["strategyType"],"successRate": template["successRate"]}
        for template in templates
    ]
    
