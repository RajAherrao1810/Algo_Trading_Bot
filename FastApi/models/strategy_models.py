from pydantic import BaseModel
from typing import List, Optional, Any, Dict


class RiskManagement(BaseModel):
    exitTime: Optional[str]
    lockProfitAt: Optional[str]=None
    lockProfitThreshold: Optional[str]=None
    lockTrailIncrease: Optional[str]=None
    lockTrailProfitBy: Optional[str]=None
    lossExit: Optional[str]
    profitExit: Optional[str]
    profitTrailingOption: Optional[str]
    trailIncrease: Optional[str]=None
    trailProfitBy: Optional[str]=None

class AdvancedFeatures(BaseModel):
    cycles: Optional[str]
    wait_trade: Optional[Dict[str, Any]]

class Strategy(BaseModel):
    advancedFeature: Optional[str]
    advancedFeatures: Optional[AdvancedFeatures]
    description: Optional[str]
    entryTime: str
    exitTime: str
    legs: List[Dict[str, Any]]
    orderType: str
    parameters: Optional[str]
    riskManagement: RiskManagement
    selectedInstrument: str
    strategyName: str
    strategyType: str


class DeployedStrategy(BaseModel):
    strategyName: str
    selectedInstrument: str
    status: str = "Running"
    overall_profit_or_loss: float = 0.0


class Order(BaseModel):
    symbol: str
    quantity: int
    avgPrice: float
    currentPrice: float
    pl: float



class FindStrategyRequest(BaseModel):
    strategyName: str
    instrument: str

