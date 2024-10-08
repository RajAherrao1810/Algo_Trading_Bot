from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import threading
import pyotp
import config
from instrument import Instrument
from pymongo import MongoClient
from logzero import logger


def login():
    obj=SmartConnect(api_key=config.API_KEY)
    data = obj.generateSession(config.USERNAME,config.PIN,pyotp.TOTP(config.TOKEN).now())
    #print(data)
    AUTH_TOKEN = data['data']['jwtToken']
    refreshToken= data['data']['refreshToken']
    FEED_TOKEN=obj.getfeedToken()
    res = obj.getProfile(refreshToken)
    
    sws = SmartWebSocketV2(AUTH_TOKEN, config.API_KEY, config.USERNAME, FEED_TOKEN ,max_retry_attempt=5)
    return obj, sws


#------- Websocket code

def get_mongo_connection():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Live_Data_Feed']
    collection = db['Live_feed']
    return collection

def on_data(wsapp, msg):
    try:
        # Parsing the incoming message (you may need to adjust the keys based on actual data)
        token = msg['token']
        ltp = msg['last_traded_price'] / 100
        open_price = msg['open_price_of_the_day'] / 100
        high = msg['high_price_of_the_day'] / 100
        low = msg['low_price_of_the_day'] / 100
        close = msg.get('closed_price', 0) / 100  # Ensure close price is provided

        # Get MongoDB collection
        collection = get_mongo_connection()

        # Check if the token already exists in the collection
        existing_token = collection.find_one({"token": token})

        if existing_token:
            # Update the existing document with new data
            collection.update_one(
                {"token": token},
                {"$set": {
                    "LTP": ltp,
                    "Open": open_price,
                    "High": high,
                    "Low": low,
                    "Cls": close,
                }}
            )
        else:
            # Insert a new document if the token is not found
            new_data = {
                
                "Symbol": Instrument.getSymbolFromToken(token),
                "token": token,
                "LTP": ltp,
                "Open": open_price,
                "High": high,
                "Low": low,
                "Cls": close,
            }
            collection.insert_one(new_data)

    except Exception as e:
        print(f"Error in on_data: {e}")


def on_error(wsapp, error):
    logger.error(f"---------Connection Error {error}-----------")

def on_close(wsapp):
    logger.info("---------Connection Close-----------")

def close_connection(sws):
    sws.MAX_RETRY_ATTEMPT = 0
    sws.close_connection()

def subscribeSymbol(token_list,sws):
    sws.subscribe(config.CORRELATION_ID, config.FEED_MODE, token_list)

def unsubscribeSymbol(token_list,sws):
    try:
        sws.unsubscribe(config.CORRELATION_ID, config.FEED_MODE, token_list)

        collection = get_mongo_connection()

        # Iterate through each token in the list
        for token in token_list:
            # Check if the token exists in the collection
            existing_token = collection.find_one({"token": token})
            if existing_token:
                # Delete the document related to this token
                collection.delete_one({"token": token})
                print(f"Deleted token {token} from MongoDB")
            else:
                print(f"Token {token} not found in MongoDB")

    except Exception as e:
        print(f"Error in unsubscribeSymbol: {e}")

def connectFeed(sws,tokeList =None):
    
    def on_open(wsapp):
        logger.info("on open")
        token_list = [
            {
                "exchangeType": 1,
                'tokens': ["26000", "26009", "26074"]
            }
        ]
        if tokeList  : token_list.append(tokeList)
        sws.subscribe(config.CORRELATION_ID, config.FEED_MODE, token_list)

    sws.on_open = on_open
    sws.on_data = on_data
    sws.on_error = on_error
    sws.on_close = on_close
    threading.Thread(target =sws.connect,daemon=True).start()




if __name__ == "__main__":
    pass


