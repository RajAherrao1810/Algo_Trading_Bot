from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import pyotp
import time
from logzero import logger

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
        'client_code':username,
        'smarApi':data,
        'authToken':authToken,
        'feedToken':feedToken
    }


# ---------- WebSocket Implementation ---------------

def webSocketImplementation():
    defs=sessionGeneration()
    AUTH_TOKEN = defs['authToken']
    API_KEY = defs['api_key']
    CLIENT_CODE = defs['client_code']
    FEED_TOKEN = defs['feedToken']


    def on_data(wsapp, message):
        logger.info("Ticks: {}".format(message))

    def on_open(wsapp):
        time.sleep(60)  # Keep the connection open for 1 minute
        logger.info("1 minute has passed, continuing...")

    def on_error(wsapp, error):
        logger.error(error)

    def on_close(wsapp):
        logger.info("WebSocket Closed")


    sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)
    # Assign the callbacks.
    sws.on_open = on_open
    sws.on_data = on_data
    sws.on_error = on_error
    sws.on_close = on_close
    return sws

if __name__=="__main__":
    webSocketImplementation()

