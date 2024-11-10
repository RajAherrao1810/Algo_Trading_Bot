# order_placement.py
from SmartApi import SmartConnect
from fastapi import HTTPException
import time
from datetime import datetime, timedelta
import functions.webSocket as webSocket
from instrument import indice_info, get_indice_ltp, get_token_symbol,get_token_from_symbol
import math
from functions import config
from Database.mongodb import live_feed, live_positions
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

def execute_strategy(strategy_dict):
    if(strategy_dict['strategyType']=='Time Based'):
        try:
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

            selected_instrument = strategy_dict["selectedInstrument"].upper()
            strategy_name=strategy_dict['strategyName']
            if strategy_dict['advancedFeature']=='Wait&Trade':
                cycles=strategy_dict['advancedFeatures']['cycles']
                symbol_list=[]
                profit_limit=strategy_dict['profitExit']
                loss_limit=strategy_dict['lossExit']
                for leg in strategy_dict["legs"]:
                    Thread(target=execute_reEntry, args=(leg, cycles, selected_instrument,symbol_list), daemon=True).start()

                strategy_exit_time=datetime.strptime(leg['exitTime'], '%H:%M').time()
                while datetime.now().time() < strategy_exit_time:
                    overall_profitorloss=get_totalProfit()
                    live_positions.update_one(
                    {'strategy_name': strategy_name, 'Instrument': selected_instrument},  # Filter for the document to update
                    {'$set': {'strategy_profit':overall_profitorloss}}  # Update operation
                    )
                    #code for handling risk management 
                    if overall_profitorloss>=profit_limit or overall_profitorloss<=loss_limit:
                        exitAllLegs(symbol_list,strategy_name,selected_instrument)
                    elif 
                        
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


def execute_reEntry(leg:dict, Instrument:str, strategy_name:str, cycles:int, symbol_list:list):
    qty=leg['lots']*indice_info()[Instrument]['lot_size']
    expiry=leg['expiry']
    european=leg['optionType']
    strike_diff=indice_info()[Instrument]['strike_diff']
    atm_strike=math.ceil(get_indice_ltp(Instrument)/strike_diff)*strike_diff  
    strike=get_strike(strike_diff,atm_strike,leg['strikePrice'],european)
    symbol=get_token_symbol(Instrument,expiry,strike,european)
    symbol_list.append[symbol]
    #subscribe the symbols and add them to the database. 
    webSocket.subscribeSymbol([get_token_from_symbol(symbol)],config.SMART_WEB)
    
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
    order_params = {
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
        print(f"Order placement failed: {str(e)}")

    #no entry after exit time
    noEntryAfter = datetime.strptime(leg['riskManagement']['exitTime'], '%H:%M').time() 
    while datetime.now().time() < noEntryAfter:
        ltp=live_feed[symbol]['LTP']
        profit=(ltp-buy_price)*qty if leg['buyOrSell']=='BUY' else (sell_price-ltp)*qty
        if(cycles==-1):
            exitAllLegs()
        elif(sl_value<=ltp or profit_target>=ltp ):
            price=exitLeg()
            total_profit=(price-buy_price)*qty if leg['buyOrSell']=='BUY' else (sell_price-price)*qty
            live_positions.update_one(
            {'strategy_name': strategy_name, 'Instrument': Instrument},  # Filter for the document to update
            {'$set': {symbol:{'total_profit':total_profit, 'qty':0}}}  # Update operation
            )
            cycles=cycles-1
            execute_reEntry(leg, Instrument, strategy_name, cycles)
        else:
            live_positions.update_one(
            {'strategy_name': strategy_name, 'Instrument': Instrument},  # Filter for the document to update
            {'$set': {symbol:{'total_profit':profit}}}  # Update operation
            )
        time.sleep(1)
        

    if live_positions.find_one({'strategy_name': strategy_name, 'Instrument': Instrument, symbol:{"symbol":symbol}}):
        strategy_exit_time=datetime.strptime(leg['exitTime'], '%H:%M').time()
        while datetime.now().time()<strategy_exit_time :
            ltp=live_feed[symbol]['LTP']
            current_profit=(ltp-buy_price)*qty if leg['buyOrSell']=='BUY' else (sell_price-ltp)*qty
            live_positions.update_one(
            {'strategy_name': strategy_name, 'Instrument': Instrument},  # Filter for the document to update
            {'$set': {symbol:{'total_profit':current_profit}}}  # Update operation
            )
            if(sl_value<=ltp or profit_target>=ltp ):
                exitAllLegs(symbol_list, strategy_name, Instrument)
            time.sleep(1)


def exitAllLegs(symbol_list:list, strategy_name:str, Instrument:str):
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
                order_id = ws.placeOrder(order_params)
                
                print(f"Order placed successfully. Order ID: {order_id}")
            except Exception as e:
                print(f"Order placement failed: {str(e)}")
            
            webSocket.unsubscribeSymbol([get_token_from_symbol(symbol)], ws)
        
    exit_event.set()  # Signal all threads to exit
            
    

def exitLeg(leg:dict,symbol:str,qty:int,Instrument:str):
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
        order_id = ws.placeOrder(order_params)
        
        print(f"Order placed successfully. Order ID: {order_id}")
    except Exception as e:
        print(f"Order placement failed: {str(e)}")
    webSocket.unsubscribeSymbol([get_token_from_symbol(symbol)], ws)
    return exit_price

def get_totalProfit(strategy_name:str,symbol_list:list):
    total_profit=0
    for symbol in symbol_list:
        total_profit+=live_positions[strategy_name][symbol]['total_profit']
    return total_profit

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