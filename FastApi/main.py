from fastapi import FastAPI, HTTPException
from models.order_models import MarketOrderRequest, LimitOrderRequest, StopLossOrderRequest
from functions.orderPlacement import PlaceOrder
import functions.webSocket as ws
from passlib.context import CryptContext
#from functions.instrument import Instrument
import functions.config as config
from fastapi.middleware.cors import CORSMiddleware
from Database.mongodb import collection
from models.register_models import UserRegister, LoginUser

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@app.get("/")
async def home():
    config.SMART_API_OBJ , config.SMART_WEB = ws.login()
    ws.connectFeed(config.SMART_WEB)
    return {"message": "Websocket connection established"}


@app.post("/register")
async def register(user: UserRegister):
    print("Registering user")
    
    # Check if email already exists in the collection
    existing_user = collection.find_one({"email": user.email})
    
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
    collection.insert_one(new_user)
    print("User added successfully")  # Confirmation that the user was added
    return {"message": "User registered successfully"}



@app.get("/login")
async def login(user: LoginUser):
    # Query the MongoDB `Users` collection
    user_data =  collection.find_one({"email": user.email})
    
    # Check if user exists and password matches
    if user_data['email']==user.email:
        hashed_pass=hash_password(user.password)
        if hashed_pass==user_data['password']:
            print('logging in')
            return {"message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid Password")
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# Route for Market Order
@app.post("/market_order")
async def place_market_order(order: MarketOrderRequest):
    try:
        PlaceOrder.normalMarketOrder(
            symbol=order.symbol,
            token=order.token,
            transaction_type=order.transaction_type,
            exchange=order.exchange,
            product_type=order.product_type,
            quantity=order.quantity,
            obj=config.SMART_API_OBJ
        )
        return {"message": "Market order placed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market order failed: {str(e)}")


# Route for Limit Order
@app.post("/limit_order")
async def place_limit_order(order: LimitOrderRequest):
    try:
        PlaceOrder.normalLimitOrder(
            symbol=order.symbol,
            token=order.token,
            transaction_type=order.transaction_type,
            exchange=order.exchange,
            product_type=order.product_type,
            limit_price=order.limit_price,
            quantity=order.quantity,
            obj=config.SMART_API_OBJ
        )
        return {"message": "Limit order placed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Limit order failed: {str(e)}")


# Route for Stop Loss Limit Order
@app.post("/stop_loss_order")
async def place_stop_loss_order(order: StopLossOrderRequest):
    try:
        PlaceOrder.stopLossLimitOrder(
            symbol=order.symbol,
            token=order.token,
            transaction_type=order.transaction_type,
            exchange=order.exchange,
            product_type=order.product_type,
            limit_price=order.limit_price,
            trigger_price=order.trigger_price,
            quantity=order.quantity,
            obj=config.SMART_API_OBJ
        )
        return {"message": "Stop Loss order placed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stop Loss order failed: {str(e)}")
