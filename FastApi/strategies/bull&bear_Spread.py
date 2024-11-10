from FastApi.instrument import Instrument
from FastApi.functions.orderPlacement import PlaceOrder
import math

class Bull_Bear_Spread():

    @classmethod
    def bull_call_spread(cls,index,expiry,lots,strike_diff):
        num=Instrument.indiceInfo()[index]['strike_diff']
        ltp=Instrument.get_indice_ltp(index)
        atm_Strike=math.ceil(ltp/num)*num   

        buy_strike=Instrument.getTokenSymbol(index,expiry,str(atm_Strike),'CE')
        sell_strike=Instrument.getTokenSymbol(index,expiry,str(atm_Strike+strike_diff*num),'CE')

        PlaceOrder.normalMarketOrder(buy_strike,str(Instrument.getTokenFromSymbol(buy_strike)),'BUY','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index][2]))
        PlaceOrder.normalMarketOrder(sell_strike,str(Instrument.getTokenFromSymbol(sell_strike)),'SELL','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index][2]))
    
    
    @classmethod
    def bear_put_spread(cls,index,expiry,lots,strike_diff):
        num=Instrument.indiceInfo()[index]['strike_diff']
        ltp=Instrument.get_indice_ltp(index)
        atm_Strike=math.ceil(ltp/num)*num   

        buy_strike=Instrument.getTokenSymbol(index,expiry,str(atm_Strike),'PE')
        sell_strike=Instrument.getTokenSymbol(index,expiry,str(atm_Strike-strike_diff*num),'PE')

        PlaceOrder.normalMarketOrder(buy_strike,str(Instrument.getTokenFromSymbol(buy_strike)),'BUY','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index][2]))
        PlaceOrder.normalMarketOrder(sell_strike,str(Instrument.getTokenFromSymbol(sell_strike)),'SELL','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index][2]))
