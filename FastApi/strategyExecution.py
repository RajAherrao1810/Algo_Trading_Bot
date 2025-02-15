# order_placement.py
from SmartApi import SmartConnect
from fastapi import HTTPException
import time
from datetime import datetime, timedelta
from functions.webSocket import subscribeSymbol, unsubscribeSymbol
from functions.instrument import indice_info, get_indice_ltp, get_token_symbol,get_token_from_symbol
import math
from functions import config
from functions.mongodb import live_feed, live_positions
from typing import Optional
from threading import Event, Thread



# Initialize SmartAPI client (make sure to authenticate and establish a session)
"""api_key = "your_api_key"
client_id = "your_client_id"
password = "your_password"

client = SmartConnect(api_key=api_key)
session = client.generateSession(client_id, password)"""


# Global exit event to signal all threads to stop
exit_event = Event()

def execute_strategy(strategy_dict,obj,sws):
    selected_instrument = strategy_dict["selectedInstrument"].upper()
    strategy_name=strategy_dict['strategyName']
    target_time = strategy_dict['entryTime']
    target_hour, target_minute = map(int, target_time.split(":"))
    now = datetime.now()

    # Calculate the target datetime for today at the specified time
    target_datetime = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

    # If the target time has already passed today, it would be set for tomorrow
    if target_datetime < now:
        target_datetime += timedelta(days=1)

        # time to wait until the target time
        time_to_wait = (target_datetime - now).total_seconds()
        # Wait until the target time
        time.sleep(time_to_wait)

    if(strategy_dict['orderType']=='Intraday'):
        strategy_exit_time=datetime.strptime(leg['exitTime'], '%H:%M').time()
        while datetime.now() < strategy_exit_time and not exit_event.is_set():
            try:
                if strategy_dict['advancedFeature']=='':
                    pass
                elif strategy_dict['advancedFeature']=='reEntry':
                    pass
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error placing order: {str(e)}")

        try:
            if strategy_dict['advancedFeature']=='':
                pass
            elif strategy_dict['advancedFeature']=='reEntry':
                cycles=strategy_dict['advancedFeatures']['cycles']
                symbol_list=[]
                profit_limit=strategy_dict['profitExit']
                loss_limit=strategy_dict['lossExit']
                for leg in strategy_dict["legs"]:
                    Thread(target=execute_reEntry, args=(leg, cycles, selected_instrument,symbol_list,sws,obj), daemon=True).start()

                strategy_exit_time=datetime.strptime(leg['exitTime'], '%H:%M').time()
                while datetime.now().time() < strategy_exit_time:
                    overall_profitorloss=get_totalProfit()
                    live_positions.update_one(
                        {'strategy_name': strategy_name, 'Instrument': selected_instrument},  # Filter for the document to update
                        {'$set': {'strategy_profit':overall_profitorloss,'book_profit':0}}  # Update operation
                        )
                    #code for handling risk management 
                    if overall_profitorloss>=profit_limit or overall_profitorloss<=loss_limit:
                        exitAllLegs(symbol_list,strategy_name,selected_instrument,obj,sws)
                    elif  strategy_dict['riskManagement']['profitTrailingOption']== 'Trail Profit':
                        increase_factor=int(strategy_dict['riskManagement']['profitIncrease'])
                        trail_factor=int(strategy_dict['riskManagement']['trailIncrease'])
                        if live_positions.find_one({'strategy_name': strategy_name, 'Instrument': selected_instrument})['book_profit']==0:
                            continue
                        elif overall_profitorloss<=live_positions.find_one({'strategy_name': strategy_name, 'Instrument': selected_instrument})['book_profit']:
                            exitAllLegs(symbol_list,strategy_name,selected_instrument,obj,sws)
                        book_profit=profit_trail(overall_profitorloss,increase_factor,trail_factor)
                        live_positions.update_one(
                        {'strategy_name': strategy_name, 'Instrument': selected_instrument},  # Filter for the document to update
                        {'$set': {'book_profit':book_profit}}  # Update operation
                        )
                    elif  strategy_dict['riskManagement']['profitTrailingOption']== 'Lock&Trail':
                        profit_reach=int(strategy_dict['riskManagement']['lockProfitThreshold'])
                        profit_lock_amount=int(strategy_dict['riskManagement']['lockProfitAt'])
                        increase_factor=int(strategy_dict['riskManagement']['lockTrailIncrease'])
                        trail_factor=int(strategy_dict['riskManagement']['lockTrailProfitBy'])
                        if live_positions.find_one({'strategy_name': strategy_name, 'Instrument': selected_instrument})['profit_lock']==0:
                            continue
                        elif overall_profitorloss<=live_positions.find_one({'strategy_name': strategy_name, 'Instrument': selected_instrument})['profit_lock']:
                            exitAllLegs(symbol_list,strategy_name,selected_instrument,obj,sws)
                        profit_lock=lock_and_trail(overall_profitorloss,profit_reach, profit_lock_amount,increase_factor, trail_factor)
                        live_positions.update_one(
                            {'strategy_name': strategy_name, 'Instrument': selected_instrument},  # Filter for the document to update
                            {'$set': {'book_profit':profit_lock}}  # Update operation
                            )       
                    time.sleep(1)
            elif strategy_dict['advancedFeature']=='waitTrade':
                pass    
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error placing order: {str(e)}")
    else:
        pass


def get_strike(strike_diff, atm_strike,strikePrice,european):
    if(strikePrice=='ATM'):
        strike=atm_strike
    else:
        factor=int(strikePrice[-1])

        if strikePrice.startswith('O') and european == 'CE':
            strike = str(int(atm_strike) + strike_diff * factor)
        elif strikePrice.startswith('O') and european == 'PE':
            strike = str(int(atm_strike) - strike_diff * factor)
        elif strikePrice.startswith('I') and european == 'CE':
            strike = str(int(atm_strike) - strike_diff * factor)
        elif strikePrice.startswith('I') and european == 'PE':
            strike = str(int(atm_strike) + strike_diff * factor)

    return strike+"00.000000"


def execute_waitTrade(leg:dict,symbol):
    ltp=live_feed.find_one({"Symbol":symbol})["LTP"]


def execute_reEntry(leg:dict, Instrument:str, strategy_name:str, cycles:int, symbol_list:list, ws,obj):
    qty=leg['lots']*indice_info()[Instrument]['lot_size']
    expiry=leg['expiry']
    european=leg['optionType']
    strike_diff=indice_info()[Instrument]['strike_diff']
    atm_strike=math.ceil(get_indice_ltp(Instrument)/strike_diff)*strike_diff  
    strike=get_strike(strike_diff,atm_strike,leg['strikePrice'],european)
    symbol=get_token_symbol(Instrument,expiry,strike,european)
    symbol_list.append[symbol]
    #subscribe the symbols and add them to the database. 
    subscribeSymbol([get_token_from_symbol(symbol)],ws)
    
    if leg['buyOrSell']=='SELL':    
        sell_price=live_feed.find_one({'Symbol':'symbol'})['LTP']
        sl_value=((100+int(leg['slPercent']))/100)*sell_price
        profit_target=((100-int(leg['epPercent']))/100)*sell_price
        live_positions.update_one(
        {'strategy_name': strategy_name, 'Instrument': Instrument},  # Filter for the document to update
        {'$set': {symbol:{"symbol":symbol,'sell_price': sell_price, 'qty':qty*(-1), 'total_profit':0}}}  # Update operation
        )
    elif leg['buyOrSell']=='BUY':    
        buy_price=live_feed.find_one({'Symbol':'symbol'})['LTP']
        sl_value=((100-int(leg['slPercent']))/100)*buy_price
        profit_target=((100+int(leg['epPercent']))/100)*buy_price
        live_positions.update_one(
        {'strategy_name': strategy_name, 'Instrument': Instrument},  # Filter for the document to update
        {'$set': {symbol:{"symbol":symbol,'buy_price': buy_price, 'qty':qty, 'total_profit':0}}}  # Update operation
        )
    #order execution on broker side
    """order_params = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,  # Token symbol (e.g., RELIANCE)
            "symboltoken": get_token_from_symbol(leg['Symbol']),
            "transactiontype": leg['buyOrSell'],  # 'BUY' or 'SELL'
            "exchange": 'BFO' if Instrument in ["SENSEX", "BANKEX"] else "NFO", 
            "ordertype": 'MARKET',  # 'MARKET', 'LIMIT', etc.
            "producttype": "INTRADAY",  # 'CNC', 'INTRADAY', etc.
            "duration": "DAY",
            "quantity": qty
        } 
    
    try:
        order_id = ws.placeOrder(order_params)
        
        print(f"Order placed successfully. Order ID: {order_id}")
    except Exception as e:
        print(f"Order placement failed: {str(e)}")"""

    #no entry after exit time
    noEntryAfter = datetime.strptime(leg['riskManagement']['exitTime'], '%H:%M').time() 
    while datetime.now().time() < noEntryAfter:
        if exit_event.set():
            return 
        ltp=live_feed[symbol]['LTP']
        profit=(ltp-buy_price)*qty if leg['buyOrSell']=='BUY' else (sell_price-ltp)*qty
        if(cycles==-1):
            exitAllLegs(symbol_list,strategy_name,Instrument,obj,ws)
        elif(sl_value<=ltp or profit_target>=ltp ):
            price=exitLeg(leg,symbol,qty,Instrument,obj, ws)
            total_profit=(price-buy_price)*qty if leg['buyOrSell']=='BUY' else (sell_price-price)*qty
            live_positions.update_one(
            {'strategy_name': strategy_name, 'Instrument': Instrument},  # Filter for the document to update
            {'$set': {symbol:{'total_profit':total_profit, 'qty':0}}}  # Update operation
            )
            cycles=cycles-1
            execute_reEntry(leg, Instrument, strategy_name, cycles,symbol_list,ws,obj)
        else:
            live_positions.update_one(
            {'strategy_name': strategy_name, 'Instrument': Instrument},  # Filter for the document to update
            {'$set': {symbol:{'total_profit':profit}}}  # Update operation
            )
        time.sleep(1)
        

    if live_positions.find_one({'strategy_name': strategy_name, 'Instrument': Instrument, symbol:{"symbol":symbol}}):
        strategy_exit_time=datetime.strptime(leg['exitTime'], '%H:%M').time()
        while datetime.now().time()<strategy_exit_time :
            if exit_event.set():
                return
            ltp=live_feed[symbol]['LTP']
            current_profit=(ltp-buy_price)*qty if leg['buyOrSell']=='BUY' else (sell_price-ltp)*qty
            live_positions.update_one(
            {'strategy_name': strategy_name, 'Instrument': Instrument},  # Filter for the document to update
            {'$set': {symbol:{'total_profit':current_profit}}}  # Update operation
            )
            if(sl_value<=ltp or profit_target>=ltp ):
                exitAllLegs(symbol_list, strategy_name, Instrument, ws, obj)
            time.sleep(1)


def exitAllLegs(symbol_list:list, strategy_name:str, Instrument:str,obj, ws):
    exit_event.set()  # Signal all threads to exit
    #exit all the open legs in the strategy
    for symbol in symbol_list:
        qty=live_positions[strategy_name][symbol]['qty']
        if qty==0:
            continue
        else:
            order_params = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,  # Token symbol (e.g., RELIANCE)
            "symboltoken": get_token_from_symbol(symbol),
            "transactiontype": 'BUY' if qty<1 else 'SELL',  # 'BUY' or 'SELL'
            "exchange": 'BFO' if Instrument in ["SENSEX", "BANKEX"] else "NFO", 
            "ordertype": 'MARKET',  # 'MARKET', 'LIMIT', etc.
            "producttype": "INTRADAY",  # 'CNC', 'INTRADAY', etc.
            "duration": "DAY",
            "quantity": qty
            } 
    
            try:
                order_id = obj.placeOrder(order_params)
                print(f"Order placed successfully. Order ID: {order_id}")
                unsubscribeSymbol([get_token_from_symbol(symbol)], ws)
            except Exception as e:
                print(f"Order placement failed: {str(e)}")
                symbol_list.append(symbol)

            
            
       
    
    live_positions.update_one(
            {'strategy_name': strategy_name, 'Instrument': Instrument},  # Filter for the document to update
            {'$set': {'status': 'closed'}}  # Update operation
            )
            
    

def exitLeg(leg:dict,symbol:str,qty:int,Instrument:str,obj, ws):
    #exit the positions
    exit_price=live_feed['symbol']['LTP']
    order_params = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,  # Token symbol (e.g., RELIANCE)
            "symboltoken": get_token_from_symbol(leg['Symbol']),
            "transactiontype": 'BUY' if leg['buyOrSell']=='Sell' else 'SELL',  # 'BUY' or 'SELL'
            "exchange": 'BFO' if Instrument in ["SENSEX", "BANKEX"] else "NFO", 
            "ordertype": 'MARKET',  # 'MARKET', 'LIMIT', etc.
            "producttype": "INTRADAY",  # 'CNC', 'INTRADAY', etc.
            "duration": "DAY",
            "quantity": qty
        } 
    
    try:
        order_id = obj.placeOrder(order_params)
        
        print(f"Order placed successfully. Order ID: {order_id}")
    except Exception as e:
        print(f"Order placement failed: {str(e)}")
    unsubscribeSymbol([get_token_from_symbol(symbol)], ws)
    return exit_price

def get_totalProfit(strategy_name:str,symbol_list:list):
    total_profit=0
    for symbol in symbol_list:
        total_profit+=live_positions[strategy_name][symbol]['total_profit']
    return total_profit

def profit_trail(overall_profit, on_every_increase, trail_by):
    # Calculate the number of increments
    increments = overall_profit // on_every_increase
    # Calculate the minimum profit to be booked
    min_profit = increments * trail_by
    return min_profit

def lock_and_trail(overall_profit, profit_reach, profit_lock, on_every_increase, trail_profit):
    # If overall profit has not reached the initial threshold, no profit should be locked
    if overall_profit < profit_reach:
        return 0  # No profit locked yet
    # Calculate how many increments of on_every_increase have been reached past profit_reach
    increments = (overall_profit - profit_reach) // on_every_increase
    # Calculate the current locked profit
    current_locked_profit = profit_lock + (increments * trail_profit)
    return current_locked_profit


if __name__ == "__main__":

    strategy_dict={'advancedFeature': 'Wait&Trade', 
                   'advancedFeatures': {'cycles': '', 'wait_trade': 
                                        {'up_percentage': '6', 
                                         'down_percentage': '7'}}, 
                    'description': '', 'entryTime': '10:15', 'exitTime': '15:15',
                    'legs': [{'buyOrSell': 'Sell', 'lots': 1, 'expiry': "27NOV2024", 'optionType': 'CE', 'strikePrice': 'OTM2', 'slPercent': '5', 'epPercent': '4'}, 
                             {'buyOrSell': 'Sell', 'lots': 1, 'expiry': "27NOV2024", 'optionType': 'PE', 'strikePrice': 'OTM1', 'slPercent': '6', 'epPercent': '5'}], 
                    'orderType': 'Intraday', 'parameters': '', 
                    'riskManagement': {'profitExit': '4567', 'lossExit': '5667', 'exitTime': '15:15', 'profitTrailingOption': 'Trail Profit', 'trailIncrease': '567'}, 
                    'selectedInstrument': 'BankNifty', 'strategyName': 'banknifty123', 'strategyType': 'Time Based'}
    execute_strategy(strategy_dict) 