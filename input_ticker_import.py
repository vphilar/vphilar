from stocksymbol import StockSymbol
import pandas as pd

api_key = '1558037d-480e-475b-a68a-cca7fac48361'
ss = StockSymbol(api_key)

#symbol_list_us = ss.get_symbol_list(market="in", symbols_only=True)
#print (len(symbol_list_us))
mkt_list = ss.market_list

completeStockDict = {}

for mkt in mkt_list:
    print ('For market: ', mkt['market'])
    symbol_list = ss.get_symbol_list(market=mkt['abbreviation'], symbols_only=True)
    completeStockDict[mkt['market']] = symbol_list
    #completeStockList.append(symbol_list_us)

print ('completeStockDict:')
print (completeStockDict)

#finalList = [item for sublist in completeStockList for item in sublist]
#print(finalList)
#resDf = pd.DataFrame(completeStockList)
#print ('resDf:')
#print (resDf[1])

#finalList = []
#for row in resDf[1]:
#    finalList.append(row)

#print ('finalList:')
resDf = pd.DataFrame.from_dict(completeStockDict, orient='index')
#resDf.columns = ['A','B']
print (resDf.head(10))
resDf.to_csv('/Users/vikramphilar/Desktop/stocklist.csv')