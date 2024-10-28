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

class Strategy(BaseModel):
    strategyName: str
    description: str
    parameters: str
    selectedInstrument: str
    strategyType: str
    orderType: str
    entryTime: str
    exitTime: str
    legs: list[Leg]
    riskManagement: RiskManagement
