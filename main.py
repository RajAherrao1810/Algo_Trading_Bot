import time
from websocket_handler import WebSocketHandler  # Custom WebSocket handler class
from instrument import Instrument  # Class containing methods to get token info, LTP, etc.
import orderPlacement  # Assuming this module handles the order placement logic
from strategies import short_Straddle, long_Straddle  # Import strategy files

# Initialize SmartAPI connection
def initialize_connection():
    api_key = "your_api_key"
    client_id = "your_client_id"
    password = "your_password"
    
    # Create SmartAPI object and login
    smart_api = SmartConnect(api_key=api_key)
    session = smart_api.generateSession(client_id, password)
    return smart_api

# Start WebSocket connection at 9:00 AM
def start_websocket_connection(smart_api):
    print("Starting WebSocket connection at 9:00 AM...")
    websocket = WebSocketHandler(smart_api)
    websocket.connect()
    return websocket

# Subscribe to the tokens based on the selected strategy
def subscribe_to_tokens(websocket, tokens):
    for token in tokens:
        websocket.subscribe(token)
    print(f"Subscribed to tokens: {tokens}")

# Fetch the latest LTP and place orders using the selected strategy
def execute_strategy(strategy_module, instrument, tokens):
    for token in tokens:
        ltp = instrument.get_ltp(token)
        print(f"Fetched LTP for token {token}: {ltp}")
        
        # Execute the strategy logic and place orders accordingly
        strategy_module.run_strategy(token, ltp)

# Main function to integrate everything
def main():
    # Step 1: Initialize SmartAPI connection
    smart_api = initialize_connection()

    # Step 2: Start WebSocket connection at 9:00 AM
    websocket = start_websocket_connection(smart_api)
    
    # Step 3: Initialize Instrument class to fetch token details
    instrument = Instrument(smart_api)
    
    # Step 4: User selects the strategy and index
    print("Select a trading strategy: 1) Short Straddle 2) Long Straddle")
    strategy_choice = input("Enter your choice (1 or 2): ")

    strategy_module = None
    if strategy_choice == '1':
        strategy_module = short_Straddle
    elif strategy_choice == '2':
        strategy_module = long_Straddle
    else:
        print("Invalid choice. Exiting...")
        return

    # Select the index to trade
    index_choice = input("Enter the index you want to trade (e.g., NIFTY, BANKNIFTY): ")
    
    # Step 5: Subscribe to the tokens based on the strategy and index
    tokens = strategy_module.get_tokens(index_choice)  # Assume each strategy module has a method to get tokens
    subscribe_to_tokens(websocket, tokens)
    
    # Step 6: Continuously fetch LTP and execute the strategy
    try:
        while True:
            execute_strategy(strategy_module, instrument, tokens)
            time.sleep(5)  # Sleep for a while before the next execution

    except KeyboardInterrupt:
        print("Shutting down WebSocket and exiting the bot...")
        websocket.disconnect()

if __name__ == "__main__":
    main()
