from instrument import Instrument
from orderPlacement import PlaceOrder
import math

class Short_StraddlexStrangle():


    @classmethod
    def short_Strangle(cls,index,expiry,lots):
        num=Instrument.indiceInfo()[index]['strike_diff']
        ltp=Instrument.get_indice_ltp(index)
        atm_Strike=str(math.ceil(ltp/num)*num)
        
        call_strike=Instrument.getTokenSymbol(index,expiry,atm_Strike,'CE')
        put_strike=Instrument.getTokenSymbol(index,expiry,atm_Strike,'PE')

        PlaceOrder.normalMarketOrder(call_strike,str(Instrument.getTokenFromSymbol(call_strike)),'SELL','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index][2]))
        PlaceOrder.normalMarketOrder(put_strike,str(Instrument.getTokenFromSymbol(put_strike)),'SELL','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index][2]))

    @classmethod
    def short_Straddle(cls,index,expiry,lots):
        num=Instrument.indiceInfo()[index]['strike_diff']
        ltp=Instrument.get_indice_ltp(index)
        atm_Strike=math.ceil(ltp/num)*num
        
        call_strike=Instrument.getTokenSymbol(index,expiry,str(atm_Strike+2*num),'CE')
        put_strike=Instrument.getTokenSymbol(index,expiry,str(atm_Strike-2*num),'PE')

        PlaceOrder.normalMarketOrder(call_strike,str(Instrument.getTokenFromSymbol(call_strike)),'SELL','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index]['lot_size']))
        PlaceOrder.normalMarketOrder(put_strike,str(Instrument.getTokenFromSymbol(put_strike)),'SELL','NFO','INTRADAY',str(lots*Instrument.indiceInfo()[index]['lot_size']))


if __name__ == "__main__":
    Short_StraddlexStrangle.short_Straddle('BANKNIFTY','25SEP24',1)