import webSocket

class PlaceOrder:

    @classmethod
    def normalMarketOrder(cls,symbol,token,transaction_type,exchange,product_type,quantity):
        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,  # Token symbol (e.g., RELIANCE)
            "symboltoken": token,
            "transactiontype": transaction_type,  # 'BUY' or 'SELL'
            "exchange": exchange,  # Can be 'NSE', 'BSE', 'MCX', etc.
            "ordertype": 'MARKET',  # 'MARKET', 'LIMIT', etc.
            "producttype": product_type,  # 'CNC', 'INTRADAY', etc.
            "duration": "DAY",
            "quantity": quantity
        }
        
        try:
            order_id = webSocket.smartApi.placeOrder(order_params)
            print(f"Order placed successfully. Order ID: {order_id}")
        except Exception as e:
            print(f"Order placement failed: {str(e)}")

    @classmethod
    def normalLimitOrder(cls,symbol,token,transaction_type,exchange,product_type,limit_price,quantity):
        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,  # Token symbol (e.g., RELIANCE)
            "symboltoken": token,
            "transactiontype": transaction_type,  # 'BUY' or 'SELL'
            "exchange": exchange,  # Can be 'NSE', 'BSE', 'MCX', etc.
            "ordertype": 'LIMIT',  # 'MARKET', 'LIMIT', etc.
            "producttype": product_type,  # 'CNC', 'INTRADAY', etc.
            "duration": "DAY",
            "price": limit_price,
            "quantity": quantity
        }
        
        try:
            order_id = webSocket.smartApi.placeOrder(order_params)
            print(f"Order placed successfully. Order ID: {order_id}")
        except Exception as e:
            print(f"Order placement failed: {str(e)}")