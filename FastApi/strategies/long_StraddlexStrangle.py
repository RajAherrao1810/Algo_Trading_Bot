from FastApi.instrument import Instrument
from FastApi.functions.orderPlacement import PlaceOrder
import math

class Long_StraddlexStrangle():

    @classmethod
    def long_Strangle(cls,index,expiry,lots,ltp,obj):
        num=Instrument.indiceInfo()[index]['strike_diff']
        atm_Strike=str(math.ceil(ltp/num)*num)
        
        call_strike=Instrument.getTokenSymbol(index,expiry,atm_Strike,'CE')
        put_strike=Instrument.getTokenSymbol(index,expiry,atm_Strike,'PE')
        call_token=str(Instrument.getTokenFromSymbol(call_strike))
        put_token=str(Instrument.getTokenFromSymbol(put_strike))

        PlaceOrder.normalMarketOrder(call_strike,call_token,'BUY','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index]['lot_size']),obj)
        PlaceOrder.normalMarketOrder(put_strike,put_token,'BUY','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index]['lot_size']),obj)

        return [{"exchangeType": 2, "tokens": [call_token ,put_token]}]
    

    @classmethod
    def long_Straddle(cls,index,expiry,lots,ltp,obj):
        num=Instrument.indiceInfo()[index]['strike_diff']
        atm_Strike=math.ceil(ltp/num)*num
        
        call_strike=Instrument.getTokenSymbol(index,expiry,str(atm_Strike+2*num),'CE')
        put_strike=Instrument.getTokenSymbol(index,expiry,str(atm_Strike-2*num),'PE')
        call_token=str(Instrument.getTokenFromSymbol(call_strike))
        put_token=str(Instrument.getTokenFromSymbol(put_strike))

        PlaceOrder.normalMarketOrder(call_strike,call_token,'BUY','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index]['lot_size']),obj)
        PlaceOrder.normalMarketOrder(put_strike,put_token,'BUY','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index]['lot_size']),obj)

        return [{"exchangeType": 2, "tokens": [call_token ,put_token]}]


if __name__ == "__main__":
    Long_StraddlexStrangle.long_Straddle('BANKNIFTY','25SEP24',1)