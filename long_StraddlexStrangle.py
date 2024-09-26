from instrument import Instrument
from orderPlacement import PlaceOrder
import math

class Long_StraddlexStrangle():

    @classmethod
    def long_Strangle(cls,index,expiry,lots):
        num=Instrument.indiceInfo()[index]['strike_diff']
        ltp=Instrument.get_indice_ltp(index)
        atm_Strike=str(math.ceil(ltp/num)*num)
        
        call_strike=Instrument.getTokenSymbol(index,expiry,atm_Strike,'CE')
        put_strike=Instrument.getTokenSymbol(index,expiry,atm_Strike,'PE')

        PlaceOrder.normalMarketOrder(call_strike,str(Instrument.getTokenFromSymbol(call_strike)),'BUY','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index]['lot_size']))
        PlaceOrder.normalMarketOrder(put_strike,str(Instrument.getTokenFromSymbol(put_strike)),'BUY','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index]['lot_size']))

    @classmethod
    def long_Straddle(cls,index,expiry,lots):
        num=Instrument.indiceInfo[index]['strike_diff']
        ltp=Instrument.get_indice_ltp(index)
        atm_Strike=math.ceil(ltp/num)*num
        
        call_strike=Instrument.getTokenSymbol(index,expiry,str(atm_Strike+2*num),'CE')
        put_strike=Instrument.getTokenSymbol(index,expiry,str(atm_Strike-2*num),'PE')

        PlaceOrder.normalMarketOrder(call_strike,str(Instrument.getTokenFromSymbol(call_strike)),'Buy','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index]['lot_size']))
        PlaceOrder.normalMarketOrder(put_strike,str(Instrument.getTokenFromSymbol(put_strike)),'BUY','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index]['lot_size']))


if __name__ == "__main__":
    Long_StraddlexStrangle.long_Straddle('BANKNIFTY','25SEP24',1)