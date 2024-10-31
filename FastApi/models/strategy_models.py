from pydantic import BaseModel
from typing import List, Optional


class Leg(BaseModel):
    buyOrSell: str
    lots: int
    expiry: str
    optionType: str
    strikePrice: float
    slPercent: float
    epPercent: float


class RiskManagement(BaseModel):
    profitExit: float
    lossExit: float
    exitTime: str


class ProfitTrailing(BaseModel):
    increase_percent: int # Percentage to increase before trailing
    trail_profit: int      # Amount to trail as profit
    profit_target:Optional[int] = None 
    profit_lock:Optional[int] = None 


class WaitTrade(BaseModel):
    up_percentage: int   # Percentage increase before waiting to trade
    down_percentage: int # Percentage decrease before waiting to trade


class AdvancedFeatures(BaseModel):
    cycles: Optional[int] = None              # Number of trade cycles
    wait_trade: Optional[WaitTrade] = None    # Wait trade configurations


class Strategy(BaseModel):
    strategyName: str
    description: str
    parameters: str
    selectedInstrument: str
    strategyType: str
    orderType: str
    entryTime: str
    exitTime: str
    legs: List[Leg]
    riskManagement: RiskManagement
    advancedFeatures: AdvancedFeatures
    trail: Optional[ProfitTrailing] = None  # Trailing profit configuration

class StrategyDeleteRequest(BaseModel):
    strategyName: str
    instrument: str
