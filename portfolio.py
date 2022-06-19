import tkinter as tk
from tkinter import messagebox
import boto
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
import tkcalendar as tkc
from boto3.dynamodb.conditions import Key, Attr


class App(customtkinter.CTk):

    WIDTH = 1200
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

        self.label_mode = customtkinter.CTkLabel(master=self.frame_left, text="Appearance Mode:")
        self.label_mode.grid(row=9, column=0, pady=0, padx=20, sticky="w")

        self.optionmenu_1 = customtkinter.CTkOptionMenu(master=self.frame_left,
                                                        values=["Light", "Dark", "System"],
                                                        command=self.change_appearance_mode)
        self.optionmenu_1.grid(row=10, column=0, pady=10, padx=20, sticky="w")

    def AddNewTrade(self):
        print("Adding a new trade")

        for widget in self.frame_right.winfo_children():
            widget.destroy()

        #self.side = customtkinter.CTkEntry(master=self.frame_right,
        #                                    width=50,
        #                                    placeholder_text="Side")
        #self.side.grid(row=1, column=1, columnspan=2, pady=20, padx=20, sticky="we")

        self.sideComboBox = customtkinter.CTkComboBox(master=self.frame_right,
                                                    values=["Buy", "Sell"])
        self.sideComboBox.grid(row=1, column=1, columnspan=1, pady=10, padx=20, sticky="we")

        self.ticker = customtkinter.CTkEntry(master=self.frame_right,
                                            width=100,
                                            placeholder_text="Ticker")
        self.ticker.grid(row=1, column=3, columnspan=2, pady=20, padx=20, sticky="we")

        self.cal = tkc.DateEntry(master=self.frame_right,
                                            width=12,
                                            borderwidth=2,
                                            foreground="black",
                                            placeholder_text="Date")
        self.cal.grid(row=1, column=5, columnspan=2, pady=20, padx=20, sticky="we")

        self.shares = customtkinter.CTkEntry(master=self.frame_right,
                                            width=100,
                                            placeholder_text="Shares")
        self.shares.grid(row=1, column=7, columnspan=2, pady=20, padx=20, sticky="we")

        self.avgPx = customtkinter.CTkEntry(master=self.frame_right,
                                            width=100,
                                            placeholder_text="Avg Price")
        self.avgPx.grid(row=1, column=9, columnspan=2, pady=20, padx=20, sticky="we")

        self.AddButton = customtkinter.CTkButton(master=self.frame_right,
                                                text="Add Trade",
                                                command=self.AddTradeToDB)
        self.AddButton.grid(row=1, column=11, pady=10, padx=20)


    def AddTradeToDB(self):
        print("Saving the following trade to DynamoDB:")
        print ('Side:', self.sideComboBox.get())
        inputTkr = self.ticker.get()
        print ('Ticker:', inputTkr)
        print ('Date:', self.cal.get())
        print ('Shares:', self.shares.get())
        print ('Avg Price:', self.avgPx.get())

        tkr = yf.Ticker(inputTkr)
        ivType = tkr.info['quoteType']

        dynRes = boto3.resource('dynamodb')
        tradesTable = dynRes.Table('TRADES')
        #print ('TRADES table size:', tradesTable.item_count)

        tradesTable.put_item(
            Item={
                    'TradeID' : str(uuid.uuid1()),
                    'Side' :  self.sideComboBox.get(),
                    'Ticker' : inputTkr,
                    'Date' : self.cal.get(),
                    'Type' : ivType,
                    'Shares' : self.shares.get(),
                    'Avg Px' : self.avgPx.get()
                }
        )
        messagebox.showinfo('Success!', 'Trade inserted in TRADES table!\n\nCurrent holdings is being updated...')
        print ('Item inserted in TRADES table!')

        response = tradesTable.scan()
        tradesDict = response['Items']
    
        while 'LastEvaluatedKey' in response:
            response = dynRes.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
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

        print ('Ticker input was', inputTkr)

        holdingsClient = boto3.client('dynamodb')

        try:

            holdingsTable = holdingsClient.describe_table(TableName='HOLDINGS')

        except holdingsClient.exceptions.ResourceNotFoundException:
            # do something here as you require

            print ('HOLDINGS table doesnt exist, so creating it...')

            # Create the DynamoDB table.
            holdingsTable = holdingsClient.create_table(
                TableName='HOLDINGS',
                BillingMode='PROVISIONED',
                KeySchema=[
                    {
                        'AttributeName': 'PositionID',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'PositionID',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )

            #holdingsTable = holdingsRes.Table('HOLDINGS')
            
        portfolioList = []

        for idx in range(0, finalTradesDf.shape[0]):

            tkr = finalTradesDf.loc[idx, 'Ticker']
            print ('Type of tkr is ', type(tkr))
            resp = holdingsClient.scan(
                TableName='HOLDINGS',
                ExpressionAttributeValues={
                    ':tkr': {
                        'S': finalTradesDf.loc[idx, 'Ticker'],
                    },
                },
                FilterExpression = 'Ticker = :tkr'
            )

            print ('resp:', resp)
            
            item = resp['Items']
            if len(item) > 0:
                print ('item exists in HOLDINGS table, please update the row for: ', item)
            else:
                print ('New item, please add to HOLDINGS table')

            print ('In here')
            ticker = yf.Ticker(tkr)
            noOfShares = float(finalTradesDf.loc[idx, 'Shares'])
            avgPx = float(finalTradesDf.loc[idx, 'Avg Px'])
            curr = ticker.info['currency']
            symbol = ticker.info['symbol']
            ivType = ticker.info['quoteType']
            lastPx = ticker.info['regularMarketPrice']
            compName = ticker.info['shortName']

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
            annualDividendIncome = noOfShares * annualDividend
            previousClosePx = ticker.info['regularMarketPreviousClose']
            movers = ((lastPx-previousClosePx)/previousClosePx)*100

            print ('Symbol:', symbol)
            print ('Shares:', noOfShares)
            print ('Avg Price:', avgPx)
            print ('Last Price:', lastPx)
            print ('Currency:', curr)
            print ('Type:', ivType)
            print ('Company Name:', compName)
            print ('Sector:', sect)
            print ('Cost Basis(USD):', costBasis)
            print ('Mkt Val(USD):', mktVal)
            print ('P/L(USD):', profitOrLoss)
            print ('P/L%:', profitOrLossPct)
            print ('Dividend Yield:', divYieldPct)
            print ('Annual Dividend:', annualDividend)
            print ('Annual Dividend Income:', annualDividendIncome)
            print ('Movers:', movers)

            print ('Inserting ', symbol, ' in HOLDINGS table')
            resp = holdingsClient.put_item(
            TableName='HOLDINGS',
            Item={
                    'PositionID' : {'S' : str(uuid.uuid1())},
                    'Symbol' : {'S' : symbol},
                    'Shares' : {'N' : str(noOfShares)},
                    'Avg Px' : {'N' : str(avgPx)},
                    'Last Price' : {'N' : str(lastPx)},
                    'Currency' : {'S' : curr},
                    'Type' : {'S' : ivType},
                    'Company Name' : {'S' : compName},
                    'Sector' : {'S' : sect},
                    'Cost Basis(USD)' : {'N' : str(costBasis)},
                    'Mkt Val(USD)' : {'N' : str(mktVal)},
                    'P/L(USD)' : {'N' : str(profitOrLoss)},
                    'P/L%' : {'N' : str(profitOrLossPct)},
                    'Dividend Yield' : {'N' : str(divYieldPct)},
                    'Annual Dividend' : {'N' : str(annualDividend)},
                    'Annual Dividend Income' : {'N' : str(annualDividendIncome)},
                    'Movers' : {'N' : str(movers)}  
                }
            )

            print ('Resp:')
            print (resp)
            
            portfolioList.append([symbol,noOfShares,avgPx,ivType,curr,lastPx,compName,sect,costBasis,mktVal,profitOrLoss,profitOrLossPct,divYieldPct,annualDividend,annualDividendIncome,movers])
            portfolioDf = pd.DataFrame(portfolioList,columns=['Symbol','Shares','Avg Px', 'Type','Currency','Last Price','Company Name','Sector','Cost Basis(USD)','Mkt Val(USD)','P/L(USD)','P/L%','Dividend Yield','Annual Dividend','Annual Dividend Income','Movers'])

        print (portfolioDf)

        messagebox.showinfo('Success!', 'HOLDINGS updated!')
        print ('HOLDINGS updated!')

    
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
        tradesDf = pd.DataFrame(tradesDict, columns=['Side','Ticker','Date','Type','Shares','Avg Px'])
        print (tradesDf)

        colList = ['Side','Ticker','Date','Type','Shares','Avg Px']

        print ('Total rows:', tradesDf.shape[0])
        print ('Total columns:', tradesDf.shape[1])

        for j in range(0,tradesDf.shape[1]):
            self.entry = tk.Entry(self.frame_right, width=20,bg='lightblue',justify='center')
            self.entry.grid(row=0, column=j)
            self.entry.insert(tk.END, colList[j])

        # An approach for creating the table
        for i in range(0,tradesDf.shape[0]):
            for j in range(0,tradesDf.shape[1]):
    
                self.entry = tk.Entry(self.frame_right, width=20, justify='center')
                self.entry.grid(row=i+1, column=j)
                self.entry.insert(tk.END, tradesDf.loc[i, tradesDf.columns[j]])


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
        holdingsDf = pd.DataFrame(holdingsDict, columns=['Symbol','Shares','Avg Px','Type','Currency','Last Price','Company Name','Sector','Cost Basis(USD)','Mkt Val(USD)','P/L(USD)','P/L%','Dividend Yield','Annual Dividend','Annual Dividend Income','Movers'])
        print (holdingsDf)
        
        colList = ['Symbol','Shares','Avg Px','Type','Currency','Last Price','Company Name','Sector','Cost Basis(USD)','Mkt Val(USD)','P/L(USD)','P/L%','Dividend Yield','Annual Dividend','Annual Dividend Income','Movers']

        for j in range(0,holdingsDf.shape[1]):
            self.entry = tk.Entry(self.frame_right, width=10,bg='lightblue',justify='center')
            self.entry.grid(row=0, column=j)
            self.entry.insert(tk.END, colList[j])

        # An approach for creating the table
        for i in range(0, holdingsDf.shape[0]):
            for j in range(0, holdingsDf.shape[1]):
       
                self.entry = tk.Entry(self.frame_right, width=10)
                self.entry.grid(row=i+1, column=j)
                self.entry.insert(tk.END, holdingsDf.loc[i, holdingsDf.columns[j]])


    def button_event(self):
        print("Button pressed")

    def change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def on_closing(self, event=0):
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
