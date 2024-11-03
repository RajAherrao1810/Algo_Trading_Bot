from pydantic import BaseModel
from typing import List, Optional, Any, Dict


class RiskManagement(BaseModel):
    profitExit: Optional[str]
    lossExit: Optional[str]
    exitTime: Optional[str]
    profitTrailingOption: Optional[str]
    trailIncrease: Optional[str]

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

