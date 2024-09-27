import threading
from webSocket import webSocketImplementation, sws,start_websocket  # Import WebSocket methods and instance
from instrument import Instrument  # Import Instrument class
import time


start_websocket()

if sws:
    ltp = Instrument.get_indice_ltp('BANKNIFTY')
    print(f'BANKNIFTY LTP: {ltp}')
else:
    print("WebSocket connection failed.")
