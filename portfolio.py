import tkinter as tk
import pandas as pd
import yfinance as yf
pd.set_option('max_columns', None)
pd.set_option("max_rows", None)


root = tk.Tk()

tradesDf = pd.read_excel('/Users/vikramphilar/Desktop/trades.xlsx')
print ('Trades List:')
print (tradesDf)

portfolioList = []

for idx, tkr in tradesDf.iterrows():
    ticker = yf.Ticker(tkr['Ticker'])
    noOfShares = tkr['#ofShares']
    avgPx = tkr['Avg Price']
    symbol = ticker.info['symbol']
    ivType = ticker.info['quoteType']
    curr = ticker.info['currency']
    lastPx = ticker.info['regularMarketPrice']
    compName = ticker.info['shortName']
    
    if ticker.info['quoteType'] == 'EQUITY':
        sector = ticker.info['sector']
        divYieldPct = ticker.info['dividendYield']
        annualDividend = ticker.info['dividendRate']
    elif ticker.info['quoteType'] == 'ETF':
        sector = 'ETF'
        divYieldPct = ticker.info['trailingAnnualDividendYield']
        annualDividend = ticker.info['trailingAnnualDividendRate']
    elif ticker.info['quoteType'] == 'MUTUALFUND':
        sector = 'MUTUALFUND'
        divYieldPct = 0
        annualDividend = 0
        
    
    costBasis = noOfShares * avgPx
    mktVal = noOfShares * lastPx
    profitOrLoss = mktVal - costBasis
    profitOrLossPct = profitOrLoss/costBasis
    annualDividendIncome = noOfShares * annualDividend
    previousClosePx = ticker.info['regularMarketPreviousClose']
    movers = ((lastPx-previousClosePx)/previousClosePx)*100

    print ('Symbol:', symbol)
    print ('Last Price:', lastPx)
    print ('Currency:', curr)
    print ('Company Name:', compName)
    print ('Sector:', sector)
    print ('Cost Basis:', costBasis)
    print ('P/L(USD):', profitOrLoss)
    print ('P/L%:', profitOrLossPct)
    print ('Dividend Yield:', divYieldPct)
    print ('Annual Dividend:', annualDividend)
    print ('Annual Dividend Income:', annualDividendIncome)
    print ('Movers:', movers)

    portfolioList.append([symbol,noOfShares,avgPx,ivType,curr,lastPx,compName,sector,costBasis,mktVal,profitOrLoss,profitOrLossPct,divYieldPct,annualDividend,annualDividendIncome,movers])
    portfolioDf = pd.DataFrame(portfolioList,columns=['Symbol','Shares','Avg Px', 'Type','Currency','Last Price','Company Name','Sector','Cost Basis(USD)','Mkt Val(USD)','P/L(USD)','P/L%','Dividend Yield','Annual Dividend','Annual Dividend Income','Movers'])

print (portfolioDf)

root.mainloop()
