from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import pyotp
from instrument import Instrument
from logzero import logger
from pymongo import MongoClient

def sessionGeneration():
    api_key = '4aontghs'
    username = 'R544080'
    pwd = '1810'
    smartApi = SmartConnect(api_key)

    try:
        token = "LLO4V5LZPZZDW2MITWEAEBPMII"
        totp = pyotp.TOTP(token).now()
    except Exception as e:
        logger.error("Invalid Token: The provided token is not valid.")
        raise e

    data = smartApi.generateSession(username, pwd, totp)

    if data['status'] == False:
        logger.error(data)
    else:
        authToken = data['data']['jwtToken']
        refreshToken = data['data']['refreshToken']
        feedToken = smartApi.getfeedToken()
        smartApi.getProfile(refreshToken)
        smartApi.generateToken(refreshToken)

    return {
        'api_key':api_key,
        'smartAPi': smartApi,
        'client_code':username,
        'authToken':authToken,
        'feedToken':feedToken
    }


# ---------- WebSocket Implementation ---------------

def webSocketImplementation(defs):
    AUTH_TOKEN = defs['authToken']
    API_KEY = defs['api_key']
    CLIENT_CODE = defs['client_code']
    FEED_TOKEN = defs['feedToken']
    

    sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)
    return sws



def feed(token_list, sws):
    correlation_id = "abc123"
    action = 1
    mode = 2

    # MongoDB connection
    client = MongoClient('mongodb://localhost:27017/')  # Replace with your actual connection string
    db = client['Live_Data_Feed']  # Database name
    collection = db['Live_feed']  # Collection name

    def on_data(wsapp, message):
        logger.info("Ticks: {}".format(message))
        token = message['token']
        ltp = message['last_traded_price'] / 100  # Dividing by 100 to handle prices in proper decimal format
        open_price = message['open_price_of_the_day'] / 100 
        high = message['high_price_of_the_day'] / 100 
        low = message['low_price_of_the_day'] / 100 
        close_price = message['closed_price'] / 100 

        # Check if the token already exists in the collection
        existing_entry = collection.find_one({"Token": token})

        if existing_entry:
            # Update the document with the new data
            collection.update_one(
                {"Token": token},
                {
                    "$set": {
                        "LTP": ltp,
                        "Open": open_price,
                        "High": high,
                        "Low": low,
                        "Cls": close_price
                    }
                }
            )
        else:
            # Insert a new document if token is not found
            new_entry = { 
                "Token": token,
                "LTP": ltp,
                "Open": open_price,
                "High": high,
                "Low": low,
                "Cls": close_price
            }
            collection.insert_one(new_entry)

    # Continue with the WebSocket implementation

    
    def on_control_message(wsapp, message):
        logger.info(f"Control Message: {message}")

    def on_open(wsapp):
        logger.info("WebSocket connection opened")
        sws.subscribe(correlation_id, mode, token_list)

    def on_error(wsapp, error):
        logger.error(error)

    def on_close(wsapp):
        logger.info("WebSocket Closed")


    
    # Assign the callbacks.
    sws.on_open = on_open
    sws.on_data = on_data
    sws.on_error = on_error
    sws.on_close = on_close
    sws.on_control_message = on_control_message
    sws.connect()
    
    

if __name__=="__main__":
    defs=sessionGeneration()
    sws=webSocketImplementation(defs)
    token_list = [
        {
            "exchangeType": 5,
            "tokens": ["244999"]
        }
    ]
    feed(token_list,sws)
    