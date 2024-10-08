import time
import webSocket
import config
import orderPlacement  

# Main function to integrate everything
def main():
    
    
    #smartApi = SmartConnect(defs['api_key']) #connection with smartApi for placing order 

    print("Select a trading strategy: 1) Short Straddle 2) Long Straddle")
    strategy_choice = input("Enter your choice (1 or 2): ")

    """strategy_module = None
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
    config.SMART_API_OBJ , config.SMART_WEB =  webSocket.login()

    webSocket.connectFeed(config.SMART_WEB)
    time.sleep(5)
    time.sleep(3)
    subscribeList  = [{"exchangeType": 2, "tokens": ["44117" ,"44118"]}]



    webSocket.subscribeSymbol(subscribeList,config.SMART_WEB)
    time.sleep(5)

    webSocket.unsubscribeSymbol(subscribeList, config.SMART_WEB)

    time.sleep(5)

    webSocket.close_connection(config.SMART_WEB)
    time.sleep(5)

    