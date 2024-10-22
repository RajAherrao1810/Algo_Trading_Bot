import time
import FastApi.functions.webSocket as webSocket
import FastApi.functions.config as config
from FastApi.strategies.short_StraddlexStrangle import Short_StraddlexStrangle

    

if __name__ == "__main__":
    config.SMART_API_OBJ , config.SMART_WEB =  webSocket.login()
    webSocket.connectFeed(config.SMART_WEB)
    time.sleep(3)
    collection=webSocket.get_mongo_connection()
    print("Select a trading strategy: 1) Short Straddle 2) Long Straddle")
    index = 'BANKNIFTY'
    expiry = '16OCT24'
    lots = 1
    ltp=collection.find_one({"Symbol": index})['LTP']
    
    #subscribeList  = [{"exchangeType": 2, "tokens": ["44117" ,"44118"]}]

    subscribeList=Short_StraddlexStrangle.short_Strangle(index,expiry,lots,ltp,config.SMART_API_OBJ)

    webSocket.subscribeSymbol(subscribeList,config.SMART_WEB)
    time.sleep(5)

    #webSocket.unsubscribeSymbol(subscribeList, config.SMART_WEB)

    

    webSocket.close_connection(config.SMART_WEB)
    time.sleep(5)

    