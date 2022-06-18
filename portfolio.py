import tkinter as tk
from tkinter import messagebox
import customtkinter 
import pandas as pd
from sqlalchemy import null
import yfinance as yf
pd.set_option('max_columns', None)
pd.set_option("max_rows", None)
import boto3
from decimal import Decimal
import uuid
import numpy as np


class App(customtkinter.CTk):

    WIDTH = 2000
    HEIGHT = 700


    def __init__(self):
        super().__init__()

        self.title("My Portfolio")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=180,
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        self.label_1 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="PORTFOLIO",
                                              text_font=("Roboto Medium", -16))  # font name and size in px
        self.label_1.grid(row=1, column=0, pady=10, padx=10)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Add New Trade",
                                                command=self.AddNewTrade)
        self.button_1.grid(row=2, column=0, pady=10, padx=20)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Show All Trades",
                                                command=self.ShowAllTrades)
        self.button_1.grid(row=3, column=0, pady=10, padx=20)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Current Holdings",
                                                command=self.CurrentHoldings)
        self.button_1.grid(row=4, column=0, pady=10, padx=20)


    def AddNewTrade(self):
        print("Adding a new trade")

        for widget in self.frame_right.winfo_children():
            widget.destroy()

        self.side = customtkinter.CTkEntry(master=self.frame_right,
                                            width=50,
                                            placeholder_text="Side")
        self.side.grid(row=1, column=1, columnspan=2, pady=20, padx=20, sticky="we")

        self.ticker = customtkinter.CTkEntry(master=self.frame_right,
                                            width=100,
                                            placeholder_text="Ticker")
        self.ticker.grid(row=1, column=3, columnspan=2, pady=20, padx=20, sticky="we")

        self.date = customtkinter.CTkEntry(master=self.frame_right,
                                            width=80,
                                            placeholder_text="Date")
        self.date.grid(row=1, column=5, columnspan=2, pady=20, padx=20, sticky="we")

        self.type = customtkinter.CTkEntry(master=self.frame_right,
                                            width=60,
                                            placeholder_text="Type")
        self.type.grid(row=1, column=7, columnspan=2, pady=20, padx=20, sticky="we")

        self.shares = customtkinter.CTkEntry(master=self.frame_right,
                                            width=100,
                                            placeholder_text="Shares")
        self.shares.grid(row=1, column=9, columnspan=2, pady=20, padx=20, sticky="we")

        self.avgPx = customtkinter.CTkEntry(master=self.frame_right,
                                            width=100,
                                            placeholder_text="Avg Price")
        self.avgPx.grid(row=1, column=11, columnspan=2, pady=20, padx=20, sticky="we")


        self.AddButton = customtkinter.CTkButton(master=self.frame_right,
                                                text="Add Trade",
                                                command=self.AddTradeToDB)
        self.AddButton.grid(row=3, column=5, pady=10, padx=20)


    def AddTradeToDB(self):
        print("Saving the following trade to DynamoDB:")
        print ('Side:', self.side.get())
        print ('Ticker:', self.ticker.get())
        print ('Date:', self.date.get())
        print ('Type:', self.type.get())
        print ('Shares:', self.shares.get())
        print ('Avg Price:', self.avgPx.get())

        tradesRes = boto3.resource('dynamodb')
        tradesTable = tradesRes.Table('TRADES')

        print ('Table size:', tradesTable.item_count)
        tradesTable.put_item(
        Item={
                'TradeID': str(uuid.uuid1()),
                'Side': self.side.get(),
                'Ticker': self.ticker.get(),
                'Date': self.date.get(),
                'Type': self.type.get(),
                'Shares': Decimal(self.shares.get()),
                'Avg Px': Decimal(self.avgPx.get())
            }
        )
        messagebox.showinfo('Success!', 'Item successfully inserted!')
        print ('Item inserted in TRADES table!')

        response = tradesTable.scan()
        tradesDict = response['Items']
    
        while 'LastEvaluatedKey' in response:
            response = tradesTable.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            tradesDict.extend(response['Items'])

        print ('All trades:')
        tradesDf = pd.DataFrame(tradesDict, columns=['TradeID','Side','Ticker','Date','Type','Shares','Avg Px'])
        print (tradesDf)

        uniqueTradesDf = tradesDf[['Side','Ticker','Type','Shares','Avg Px']]
        uniqueTradesDf['Shares'] = uniqueTradesDf['Shares'].astype('float64')
        uniqueTradesDf['Avg Px'] = uniqueTradesDf['Avg Px'].astype('float64')

        print ('Before uniqueTradesDf:')
        print (uniqueTradesDf)
        uniqueTradesGrpDf = uniqueTradesDf.groupby(['Side','Ticker'])
        #uniqueTradesGrpDf['Sum Product'] = uniqueTradesGrpDf['Shares'] * uniqueTradesGrpDf['Avg Px']
        print ('After modify of uniqueTradesDf:')
        print (uniqueTradesGrpDf)

        uniqTradesList = []

        for grp, df in uniqueTradesGrpDf:
            print ('grp:', grp)
            print (df)

            df['Sum Prod'] = df['Shares'] * df['Avg Px']
            finalAvgPx = np.sum(df['Sum Prod']) / np.sum(df['Shares'])
            print ('grp:', grp)
            print ('Total Shares:', np.sum(df['Shares']))
            print ('Final Avg Px:', finalAvgPx)
            uniqTradesList.append((grp[0], grp[1], np.sum(df['Shares']), finalAvgPx))
        
        print ('uniqTradesList:')
        print (uniqTradesList)

        uniqueTradesDf = pd.DataFrame(uniqTradesList, columns=['Side','Ticker','Shares','Avg Px'])
        print (uniqueTradesDf) 
        tmpAvgPxDf = uniqueTradesDf[uniqueTradesDf['Side']=='Buy']
        print ('tmpAvgPxDf:')
        print (tmpAvgPxDf)
        tmpAvgPxDf = tmpAvgPxDf[['Side','Ticker','Avg Px']]
        uniqueTradesDf['Shares'] = np.where(uniqueTradesDf['Side'] == 'Sell', uniqueTradesDf['Shares'] * -1, uniqueTradesDf['Shares'])
        uniqueTradesDf = uniqueTradesDf[['Side', 'Ticker','Shares','Avg Px']]
        uniqueTradesDf = uniqueTradesDf.groupby(['Ticker'])['Shares'].sum().reset_index()
        print (uniqueTradesDf)

        finalTradesDf = pd.merge(tmpAvgPxDf, uniqueTradesDf, on=['Ticker'], how='inner')
        print ('finalTradesDf:')
        print (finalTradesDf)

        tradesDict = finalTradesDf.to_dict()
        print ('tradesDict:')
        print (tradesDict)

        portfolioList = []

        for idx in range(0, finalTradesDf.shape[0]):
            ticker = yf.Ticker(finalTradesDf.iloc[idx, 'Ticker'])
            noOfShares = float(finalTradesDf.iloc[idx, 'Shares'])
            avgPx = float(finalTradesDf.iloc[idx, 'Avg Px'])
            curr = ticker.info['currency']
            symbol = ticker.info['symbol']
            ivType = ticker.info['quoteType']
            lastPx = ticker.info['regularMarketPrice']
            compName = ticker.info['shortName']
            print ('compName:', compName)

            if ticker.info['quoteType'] == 'EQUITY':
                sect = ticker.info['sector']
                if ticker.info['dividendYield'] == None:
                    divYieldPct = 0
                else:
                    divYieldPct = ticker.info['dividendYield']
                if ticker.info['dividendRate'] == None:
                    annualDividend = 0
                else:
                    annualDividend = ticker.info['dividendRate']
            elif ticker.info['quoteType'] == 'ETF':
                sect = 'ETF'
                if ticker.info['trailingAnnualDividendYield'] == None:
                    divYieldPct = 0
                else:
                    divYieldPct = ticker.info['trailingAnnualDividendYield']
                
                if ticker.info['trailingAnnualDividendRate'] == None:
                    annualDividend = 0
                else:
                    annualDividend = ticker.info['trailingAnnualDividendRate']
            elif ticker.info['quoteType'] == 'MUTUALFUND':
                sect = 'MUTUALFUND'
                divYieldPct = 0
                annualDividend = 0
            
            costBasis = noOfShares * avgPx
            mktVal = noOfShares * lastPx
            profitOrLoss = mktVal - costBasis
            profitOrLossPct = profitOrLoss/costBasis
            print ('annualDividend:', annualDividend)
            print ('noOfShares:', noOfShares)
            annualDividendIncome = noOfShares * annualDividend
            previousClosePx = ticker.info['regularMarketPreviousClose']
            movers = ((lastPx-previousClosePx)/previousClosePx)*100

            print ('Symbol:', symbol)
            print ('Last Price:', lastPx)
            print ('Currency:', curr)
            print ('Type:', type)
            print ('Company Name:', compName)
            print ('Sector:', sect)
            print ('Cost Basis:', costBasis)
            print ('P/L(USD):', profitOrLoss)
            print ('P/L%:', profitOrLossPct)
            print ('Dividend Yield:', divYieldPct)
            print ('Annual Dividend:', annualDividend)
            print ('Annual Dividend Income:', annualDividendIncome)
            print ('Movers:', movers)

            portfolioList.append([symbol,noOfShares,avgPx,ivType,curr,lastPx,compName,sect,costBasis,mktVal,profitOrLoss,profitOrLossPct,divYieldPct,annualDividend,annualDividendIncome,movers])
            portfolioDf = pd.DataFrame(portfolioList,columns=['Symbol','Shares','Avg Px', 'Type','Currency','Last Price','Company Name','Sector','Cost Basis(USD)','Mkt Val(USD)','P/L(USD)','P/L%','Dividend Yield','Annual Dividend','Annual Dividend Income','Movers'])

        print (portfolioDf)
      
       
    
    def ShowAllTrades(self):

        for widget in self.frame_right.winfo_children():
            widget.destroy()

        print("Extract Trades from DynamoDB and display:")

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('TRADES')

        response = table.scan()
        tradesDict = response['Items']
    
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            tradesDict.extend(response['Items'])
        
        print (tradesDict)

        print ('List of all trades:')
        tradesDf = pd.DataFrame(tradesDict, columns=['TradeID','Side','Ticker','Date','Type','Shares','Avg Px'])
        print ('Current Trades:')
        print (tradesDf)

        colList = ['TradeID','Side','Ticker','Date','Type','Shares','Avg Px']

        # An approach for creating the table
        for i in range(tradesDf.shape[0]):
            for j in range(tradesDf.shape[1]):
                print(i)
       
                self.entry = tk.Entry(self.frame_right, width=20)
                self.entry.grid(row=i, column=j)
                if i==0:
                    self.entry.insert(tk.END, colList[j])
                else:  
                    self.entry.insert(tk.END, tradesDf.values.tolist()[i][j])


    def CurrentHoldings(self):
        print("Get Current Holdings")

        for widget in self.frame_right.winfo_children():
            widget.destroy()

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('HOLDINGS')

        response = table.scan()
        holdingsDict = response['Items']
    
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            holdingsDict.extend(response['Items'])
        
        print (holdingsDict)

        print ('Current Holdings:')
        holdingsDf = pd.DataFrame(holdingsDict, columns=['Symbol','Shares','Avg Px', 'Type','Currency','Last Price','Company Name','Sector','Cost Basis(USD)','Mkt Val(USD)','P/L(USD)','P/L%','Dividend Yield','Annual Dividend','Annual Dividend Income','Movers'])
        print (holdingsDf)
        


    
        # ============ frame_info ============

        #self.frame_info = customtkinter.CTkFrame(master=self.frame_right)
        #self.frame_info.grid(row=0, column=0, columnspan=4, rowspan=4, pady=20, padx=20, sticky="nsew")

        # configure grid layout (1x1)
        #self.frame_info.rowconfigure(0, weight=1)
        #self.frame_info.columnconfigure(0, weight=1)

        portfolioList = []
        colsList = portfolioDf.columns.tolist()
        portfolioList.append(colsList)
        portfolioList.append(portfolioDf.values.tolist())

        print ('portfolioList:', portfolioList)

        for i in range(portfolioDf.shape[0]):
            for j in range(portfolioDf.shape[1]):

                self.e = customtkinter.CTkEntry(master=self.frame_right,
                                                width=90,
                                                fg='blue')

                self.e.grid(row=i, column=j)
                self.e.insert(tk.END, portfolioList[i][j])


    def button_event(self):
        print("Button pressed")

    def change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def on_closing(self, event=0):
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
