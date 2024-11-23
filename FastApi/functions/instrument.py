import requests
import pandas as pd
from functions.mongodb import masterList, live_feed

def get_master_list():
    # Fetch the JSON data
    url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    data = requests.get(url).json()
    
    # Convert JSON to DataFrame
    tokendf = pd.DataFrame.from_dict(data)
    
    # Filter the DataFrame for 'exchange_seg' being 'NFO' or 'BFO'
    filtered_tokendf = tokendf[(tokendf['exch_seg'].isin(['NFO', 'BFO'])) & (tokendf['instrumenttype'] == 'OPTIDX')]
    
    # Convert filtered DataFrame to dictionary and insert into MongoDB
    masterList.delete_many({})  # Clear existing data in MasterList (if needed)
    masterList.insert_many(filtered_tokendf.to_dict("records"))


def get_token_from_symbol(symbol):
    token_data = masterList.find_one({"symbol": symbol})

    # Return the 'token' if the symbol was found, otherwise return None
    if token_data:
        return token_data['token']
    else:
        return None

def get_symbol_from_token(token):
    token_data = masterList.find_one({"token": token})
    
    if token_data:
        return token_data['symbol']
    else:
        return None

def get_token_symbol(index, expiry, strike, european):
    query = {
        'name': index.upper(),
        'strike': strike,
        'expiry': expiry,
        'symbol': {"$regex": european + "$"}
    }
    data=masterList.find_one(query)
    if data:
        return data['symbol']
    else:
        print('symbol not found')

def indice_info():
    index_info = {
        'SENSEX': {'strike_diff': 100, 'token': '500209', 'lot_size': 10},
        'BANKNIFTY': {'strike_diff': 100, 'token': '26009', 'lot_size': 15},
        'BANKEX': {'strike_diff': 100, 'token': '500253', 'lot_size': 15},
        'NIFTY': {'strike_diff': 50, 'token': '26000', 'lot_size': 25},
        'FINNIFTY': {'strike_diff': 50, 'token': '999260', 'lot_size': 25},
        'MIDCPNIFTY': {'strike_diff': 25, 'token': '26164', 'lot_size': 50}
    }
    return index_info

def get_indice_ltp(index):
    return live_feed.find_one({'Symbol':index.upper()})['LTP']
    

if __name__ == "__main__":
    # token = get_token_from_symbol('BANKNIFTY25SEP2454000CE')
    # print(token)
    # print(get_token_symbol('BANKNIFTY', '25SEP24', '54000', 'CE'))
    # print(get_indice_ltp('BANKNIFTY'))
    get_master_list()
    #get_token_symbol("Nifty", '21NOV2024', '24400', 'CE')
    #get_indice_ltp('Nifty')
