import requests
import pandas as pd

class Instrument():
    
    @classmethod
    def getMasterList(cls):
        url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
        d = requests.get(url).json()
        tokendf =pd.DataFrame.from_dict(d)
        tokendf.to_csv("MasterList.csv", index=False)

    @classmethod
    def getTokenFromSymbol(cls, symbol):
        master_df = pd.read_csv('MasterList.csv', low_memory=False)
        token_row = master_df.loc[master_df['symbol'] == symbol]
        
        if not token_row.empty:
            return token_row.iloc[0]['token']
        else:
            return None
        
    @classmethod
    def getSymbolFromToken(cls, token):
        master_df = pd.read_csv('MasterList.csv', low_memory=False)
        token_row = master_df.loc[master_df['token'] == token]
        
        if not token_row.empty:
            return token_row.iloc[0]['symbol']
        else:
            return None

        
    @classmethod
    def getTokenSymbol(cls,index,expiry,strike,european):
        return index+expiry+strike+european

    @classmethod
    def indiceInfo(cls):
        index_info={
        'SENSEX': {'strike_diff': 100, 'token': '500209', 'lot_size': 10},
        'BANKNIFTY': {'strike_diff': 100, 'token': '26009', 'lot_size': 15},
        'BANKEX': {'strike_diff': 100, 'token': '500253', 'lot_size': 15},
        'NIFTY': {'strike_diff': 50, 'token': '26000', 'lot_size': 25},
        'FINNIFTY': {'strike_diff': 50, 'token': '999260', 'lot_size': 25},
        'MIDCPNIFTY': {'strike_diff': 25, 'token': '26164', 'lot_size': 50}
    }
        return index_info
    
    @classmethod
    def get_indice_ltp(cls,index):
        pass

if __name__ == "__main__":
    #token=Instrument.getTokenFromSymbol('BANKNIFTY25SEP2454000CE')
    #print(token)
    #print(Instrument.getTokenSymbol('BANKNIFTY','25SEP24','54000','CE'))
    #print(Instrument.get_indice_ltp('BANKNIFTY'))
    Instrument.getMasterList()