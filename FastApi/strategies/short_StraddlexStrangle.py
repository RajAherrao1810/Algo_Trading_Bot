from FastApi.instrument import Instrument
from FastApi.functions.orderPlacement import PlaceOrder
import math

class Short_StraddlexStrangle():

    @classmethod
    def short_Strangle(cls,index,expiry,lots,ltp,obj):
        num=Instrument.indiceInfo()[index]['strike_diff']
        atm_Strike=str(math.ceil(ltp/num)*num)
        
        call_strike=Instrument.getTokenSymbol(index,expiry,atm_Strike,'CE')
        put_strike=Instrument.getTokenSymbol(index,expiry,atm_Strike,'PE')
        call_token=str(Instrument.getTokenFromSymbol(call_strike))
        put_token=str(Instrument.getTokenFromSymbol(put_strike))

        PlaceOrder.normalMarketOrder(call_strike,call_token,'SELL','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index]['lot_size']),obj)
        PlaceOrder.normalMarketOrder(put_strike,put_token,'SELL','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index]['lot_size']),obj)

        return [{"exchangeType": 2, "tokens": [call_token ,put_token]}]

    @classmethod
    def short_Straddle(cls,index,expiry,lots,ltp,obj):
        num=Instrument.indiceInfo()[index]['strike_diff']
        atm_Strike=math.ceil(ltp/num)*num
        
        call_strike=Instrument.getTokenSymbol(index,expiry,str(atm_Strike+2*num),'CE')
        put_strike=Instrument.getTokenSymbol(index,expiry,str(atm_Strike-2*num),'PE')
        call_token=str(Instrument.getTokenFromSymbol(call_strike))
        put_token=str(Instrument.getTokenFromSymbol(put_strike))

        PlaceOrder.normalMarketOrder(call_strike,call_token,'SELL','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index]['lot_size']),obj)
        PlaceOrder.normalMarketOrder(put_strike,put_token,'SELL','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index]['lot_size']),obj)

        return [{"exchangeType": 2, "tokens": [call_token ,put_token]}]

if __name__ == "__main__":
    Short_StraddlexStrangle.short_Strangle('BANKNIFTY','09OCT24',1,51021)