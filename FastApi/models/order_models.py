from pydantic import BaseModel

class MarketOrderRequest(BaseModel):
    symbol: str
    token: str
    transaction_type: str  # BUY or SELL
    exchange: str          # e.g., NSE, BSE
    product_type: str      # e.g., CNC, INTRADAY
    quantity: int

class LimitOrderRequest(BaseModel):
    symbol: str
    token: str
    transaction_type: str  # BUY or SELL
    exchange: str          # e.g., NSE, BSE
    product_type: str      # e.g., CNC, INTRADAY
    limit_price: float
    quantity: int

class StopLossOrderRequest(BaseModel):
    symbol: str
    token: str
    transaction_type: str  # BUY or SELL
    exchange: str          # e.g., NSE, BSE
    product_type: str      # e.g., CNC, INTRADAY
    limit_price: float
    trigger_price: float
    quantity: int
