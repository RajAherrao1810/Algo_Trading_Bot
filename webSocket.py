from SmartApi import SmartConnect 
#from SmartApi.smartConnect import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import pyotp
from logzero import logger

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

correlation_id = "abcde"
data = smartApi.generateSession(username, pwd, totp)

if data['status'] == False:
    logger.error(data)
    
else:
    # login api call
    # logger.info(f"You Credentials: {data}")
    authToken = data['data']['jwtToken']
    refreshToken = data['data']['refreshToken']
    # fetch the feedtoken
    feedToken = smartApi.getfeedToken()
    # fetch User Profile
    res = smartApi.getProfile(refreshToken)
    smartApi.generateToken(refreshToken)
    res=res['data']['exchanges']


#----------  Web Socket Implementation---------------

def webSocketImplementation():
    AUTH_TOKEN = authToken
    API_KEY = api_key
    CLIENT_CODE = username
    FEED_TOKEN = feedToken
    correlation_id = "abc123"
    action = 1
    mode = 1

    token_list = [
        {
            "exchangeType": 1,
            "tokens": ["26009"]
        }
    ]
    token_list1 = [
        {
            "action": 0,
            "exchangeType": 1,
            "tokens": ["26009"]
        }
    ]

    sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)

    def on_data(wsapp, message):
        logger.info("Ticks: {}".format(message))
        # close_connection()

    def on_open(wsapp):
        logger.info("on open")
        sws.subscribe(correlation_id, mode, token_list)
        # sws.unsubscribe(correlation_id, mode, token_list1)


    def on_error(wsapp, error):
        logger.error(error)


    def on_close(wsapp):
        logger.info("Close")



    def close_connection():
        sws.close_connection()


    # Assign the callbacks.
    sws.on_open = on_open
    sws.on_data = on_data
    sws.on_error = on_error
    sws.on_close = on_close

    sws.connect()