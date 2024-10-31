# strategyExecution.py
from datetime import datetime
import asyncio
from typing import List, Optional



# Define classes for the strategy components
class Leg:
    def __init__(self, script: str, action: str, strike_price: float, stop_loss: float):
        self.script = script
        self.action = action
        self.strike_price = strike_price
        self.stop_loss = stop_loss

class RiskManagement:
    def __init__(self, profit_target: float, loss_target: float):
        self.profit_target = profit_target
        self.loss_target = loss_target

class AdvancedFeatures:
    def __init__(self, reentry_cycles: Optional[int] = None, wait_trade_up_condition: Optional[str] = None,
                 wait_trade_down_condition: Optional[str] = None):
        self.reentry_cycles = reentry_cycles
        self.wait_trade_up_condition = wait_trade_up_condition
        self.wait_trade_down_condition = wait_trade_down_condition

class ProfitTrailing:
    def __init__(self, lock_value: Optional[int] = None, trailing_value: Optional[int] = None):
        self.lock_value = lock_value
        self.trailing_value = trailing_value

class Strategy:
    def __init__(self, strategyName: str, parameters: str, selectedInstrument: str, strategyType: str,
                 orderType: str, entryTime: str, exitTime: Optional[str], legs: List[Leg],
                 riskManagement: RiskManagement, advancedFeatures: Optional[AdvancedFeatures] = None,
                 trail: Optional[ProfitTrailing] = None):
        self.strategyName = strategyName
        self.parameters = parameters
        self.selectedInstrument = selectedInstrument
        self.strategyType = strategyType
        self.orderType = orderType
        self.entryTime = datetime.strptime(entryTime, "%H:%M")
        self.exitTime = datetime.strptime(exitTime, "%H:%M") if exitTime else None
        self.legs = legs
        self.riskManagement = riskManagement
        self.advancedFeatures = advancedFeatures
        self.trail = trail

async def execute_strategy(strategy: Strategy, collection):
    current_profit = 0
    trade_active = True

    # Wait until entry time to start the strategy
    while datetime.now().time() < strategy.entryTime.time():
        await asyncio.sleep(10)

    # Execute each leg of the strategy
    for leg in strategy.legs:
        order_response = place_order(leg.script, leg.action, leg.strike_price, leg.stop_loss)
        if order_response["status"] != "success":
            print(f"Order failed for {leg.script}")
            return
        
        # Log order in MongoDB
        collection.Live_feed.insert_one({
            "strategyName": strategy.strategyName,
            "action": leg.action,
            "script": leg.script,
            "strike_price": leg.strike_price,
            "time": datetime.now(),
            "status": "Entered"
        })

    # Monitor Profit/Loss Targets
    while trade_active:
        current_ltp = fetch_ltp(strategy.selectedInstrument)
        current_profit = calculate_profit(strategy.legs, current_ltp)

        if current_profit >= strategy.riskManagement.profit_target:
            close_positions(strategy)
            trade_active = False
            collection.Live_feed.update_one({"strategyName": strategy.strategyName}, {"$set": {"status": "Profit Target Reached"}})
            break

        if current_profit <= -strategy.riskManagement.loss_target:
            close_positions(strategy)
            trade_active = False
            collection.Live_feed.update_one({"strategyName": strategy.strategyName}, {"$set": {"status": "Loss Target Reached"}})
            break

        await asyncio.sleep(5)

    # Advanced Features (Re-entry cycles)
    if strategy.advancedFeatures and strategy.advancedFeatures.reentry_cycles:
        for cycle in range(strategy.advancedFeatures.reentry_cycles):
            if not trade_active:
                break
            # Add re-entry conditions logic here

    # Trailing Profit (Lock & Trail)
    if strategy.trail:
        if current_profit > strategy.trail.lock_value:
            trailing_stop = current_profit - strategy.trail.trailing_value
            # Update stop loss if profit decreases by trailing_value

    return {"message": "Strategy execution complete"}

# Helper functions for trading and calculations
def place_order(script, action, price, stop_loss):
    # Pseudo code for placing an order (replace with actual API logic)
    return {"status": "success", "order_id": "sample_order_id"}

def fetch_ltp(instrument):
    # Placeholder function for fetching last traded price (LTP)
    return 100  # Replace with actual LTP retrieval logic

def calculate_profit(legs, current_ltp):
    # Placeholder function for calculating profit based on LTP and legs
    return 50  # Replace with actual profit calculation logic

def close_positions(strategy):
    # Logic to close all positions in the strategy
    pass
