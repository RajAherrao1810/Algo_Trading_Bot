from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import pyotp
from datetime import datetime, time
from logzero import logger
import threading
import time as sleep_time

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


# ---------- WebSocket Implementation ---------------

def webSocketImplementation():
    global sws  # Global WebSocket instance
    AUTH_TOKEN = authToken
    API_KEY = api_key
    CLIENT_CODE = username
    FEED_TOKEN = feedToken

    if not sws:
        sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)

    def on_data(wsapp, message):
        logger.info("Ticks: {}".format(message))

    def on_open(wsapp):
        logger.info("WebSocket Opened")

    def on_error(wsapp, error):
        logger.error(error)

    def on_close(wsapp):
        logger.info("WebSocket Closed")

    # Assign the callbacks.
    sws.on_open = on_open
    sws.on_data = on_data
    sws.on_error = on_error
    sws.on_close = on_close

    now = datetime.now().time()
    if time(9, 15) <= now <= time(15, 30):
        logger.info("Within market hours, WebSocket connecting...")
        sws.connect()

        while time(9, 15) <= datetime.now().time() <= time(15, 30):
            sleep_time.sleep(5)  # Sleep for 5 seconds to keep thread alive
        logger.info("Market hours over. Disconnecting WebSocket.")
        sws.close_connection()


# Start WebSocket in a daemon thread so it stays active in the background
def start_websocket():
    websocket_thread = threading.Thread(target=webSocketImplementation)
    websocket_thread.daemon = True  # Runs in the background
    websocket_thread.start()

