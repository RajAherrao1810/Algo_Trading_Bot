from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')

# Defining Database and Collection
strategy_db = client['Strategies']
strategy_temp = strategy_db['Strategy_Templates']

strategyName = "1 % SL strangle BNF"
selectedInstrument = "BankNifty"

# Fetch the document
document = strategy_temp.find_one({'strategyName': strategyName, 'selectedInstrument': selectedInstrument})

if document:
    # Remove the `_id` field to avoid duplication error
    document.pop('_id', None)
    
    # Add the `successRate` field
    document['successRate'] = 59
    
    # Insert the modified document
    strategy_temp.insert_one(document)
else:
    print("No matching document found.")



"""
strategy={'advancedFeature': '', 
                   'advancedFeatures': {'cycles': '', 'wait_trade': 
                                        {'up_percentage': '', 
                                         'down_percentage': ''}}, 
                    'description': '', 'entryTime': '09:20', 'exitTime': '15:15',
                    'legs': [{'buyOrSell': 'Buy', 'lots': 1, 'expiry': "27NOV2024", 'optionType': 'PE', 'strikePrice': 'ATM', 'slPercent': '30%', 'epPercent': ''}, 
                             {'buyOrSell': 'Sell', 'lots': 2, 'expiry': "27NOV2024", 'optionType': 'PE', 'strikePrice': 'OTM2', 'slPercent': '30%', 'epPercent': ''}], 
                    'orderType': 'Intraday', 'parameters': '', 
                    'riskManagement': {'profitExit': '15000', 'lossExit': '3000', 'exitTime': '15:10', 'profitTrailingOption': 'No Trailing'}, 
                    'selectedInstrument': 'Nifty', 'strategyName': 'Iron Condor', 'strategyType': 'Time Based'}"""


#strategy_temp.insert_one(strategy)