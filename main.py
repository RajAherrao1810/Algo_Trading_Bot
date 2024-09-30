import time
import webSocket
from SmartApi import SmartConnect
import threading
import orderPlacement  


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
    defs=webSocket.sessionGeneration()

    #connection with websocket to generate ltp of indices
    """websocket_thread = threading.Thread(target=webSocket.webSocketImplementation(defs))
    websocket_thread.daemon = True  # Set the thread as a daemon
    websocket_thread.start()"""
    
    smartApi = SmartConnect(defs['api_key'])


    """
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
        websocket.disconnect()"""

if __name__ == "__main__":
    main()
 