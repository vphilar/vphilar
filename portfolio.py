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


    def CheckIfTableExists(self, tableName):
        dynDBRes = boto3.client('dynamodb')
        tablesDict = dynDBRes.list_tables()
        print ('tablesDict:', tablesDict['TableNames'])
        tablesList = tablesDict['TableNames']

        if tableName in tablesList:
            print (tableName + ' table exists! No need to create one')
            return (True)
        else:
            print (tableName + ' table doesnt exist! Creating a new one...')
            return (False)




    def AddTradeToDB(self):
        print("Saving the following trade to DynamoDB:")
        print ('Side:', self.sideComboBox.get())
        inputTkr = self.ticker.get()
        print ('Ticker:', inputTkr)
        print ('Date:', self.cal.get())
        print ('Shares:', self.shares.get())
        print ('Avg Price:', self.avgPx.get())

        tkr = yf.Ticker(inputTkr).info
        ivType = tkr.get('quoteType')

        tableExists = self.CheckIfTableExists('TRADES')

        if tableExists:
            tradesRes = boto3.resource('dynamodb')
            tradesTable = tradesRes.Table('TRADES')
        else:
            # Create the DynamoDB table.
            tradesRes = boto3.resource('dynamodb')
            tradesTable = tradesRes.create_table(
                TableName='TRADES',
                BillingMode='PROVISIONED',
                KeySchema=[
                    {   
                        'AttributeName': 'TradeID',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'TradeID',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
        
        tradesTable.wait_until_exists()
        
        tradesTable.put_item(
            TableName='TRADES',
            Item={
                    'TradeID' : str(uuid.uuid1()),
                    'Side' :  self.sideComboBox.get(),
                    'Ticker' : inputTkr,
                    'Date' : self.cal.get(),
                    'IVType' : ivType,
                    'Shares' : self.shares.get(),
                    'Avg Px' : self.avgPx.get()
                }
            )

        messagebox.showinfo('Success!', 'Trade inserted in TRADES table!\n\nUpdating holdings table...')
        print ('Item inserted in TRADES table!')

        resp = tradesTable.scan()
        tradesDict = resp['Items']
    
        while 'LastEvaluatedKey' in resp:
            resp = tradesRes.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
            tradesDict.extend(resp['Items'])

        print ('All trades:')
        tradesDf = pd.DataFrame(tradesDict, columns=['TradeID','Side','Ticker','Date','IVType','Shares','Avg Px'])
        print (tradesDf)

        uniqueTradesDf = tradesDf[['Side','Ticker','IVType','Shares','Avg Px']]
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

        tableExists = self.CheckIfTableExists('HOLDINGS')

        if tableExists:
            holdingsRes = boto3.resource('dynamodb')
            holdingsTable = holdingsRes.Table('HOLDINGS')
        else:
            # Create the DynamoDB table.
            holdingsRes = boto3.resource('dynamodb')
            holdingsTable = holdingsRes.create_table(
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
            holdingsTable.wait_until_exists()
            

        portfolioList = []

        for idx in range(0, finalTradesDf.shape[0]):

            stock = finalTradesDf.loc[idx, 'Ticker']

            print ('In here')
            ticker = yf.Ticker(stock).info
            noOfShares = float(finalTradesDf.loc[idx, 'Shares'])
            avgPx = float(finalTradesDf.loc[idx, 'Avg Px'])
            curr = ticker.get('currency')
            symbol = ticker.get('symbol')
            ivType = ticker.get('quoteType')
            lastPx = ticker.get('regularMarketPrice')
            compName = ticker.get('shortName')

            if ticker.get('quoteType') == 'EQUITY':

                if ticker.get('sector'):
                    sect = ticker.get('sector')
                else:
                    sect = None

                if ticker.get('dividendYield') == None:
                    divYieldPct = 0
                else:
                    divYieldPct = ticker.get('dividendYield')
                if ticker.get('dividendRate') == None:
                    annualDividend = 0
                else:
                    annualDividend = ticker.get('dividendRate')
            elif ticker.get('quoteType') == 'ETF':
                sect = 'ETF'
                if ticker.get('trailingAnnualDividendYield') == None:
                    divYieldPct = 0
                else:
                    divYieldPct = ticker.get('trailingAnnualDividendYield')
                
                if ticker.get('trailingAnnualDividendRate') == None:
                    annualDividend = 0
                else:
                    annualDividend = ticker.get('trailingAnnualDividendRate')
            elif ticker.get('quoteType') == 'MUTUALFUND':
                sect = 'MUTUALFUND'
                divYieldPct = 0
                annualDividend = 0
            
            costBasis = noOfShares * avgPx
            mktVal = noOfShares * lastPx
            profitOrLoss = mktVal - costBasis
            profitOrLossPct = profitOrLoss/costBasis
            annualDividendIncome = noOfShares * annualDividend
            previousClosePx = ticker.get('regularMarketPreviousClose')
            movers = ((lastPx-previousClosePx)/previousClosePx)*100

            print ('Symbol:', symbol)
            print ('Shares:', noOfShares)
            print ('Avg Px:', avgPx)
            print ('Last Price:', lastPx)
            print ('Currency:', curr)
            print ('IVType:', ivType)
            print ('Company Name:', compName)
            print ('Sector:', sect)
            print ('Cost Basis(USD):', costBasis)
            print ('Mkt Val(USD):', mktVal)
            print ('ProfitLossUSD:', profitOrLoss)
            print ('ProfitLossPct:', profitOrLossPct)
            print ('Dividend Yield:', divYieldPct)
            print ('Annual Dividend:', annualDividend)
            print ('Annual Dividend Income:', annualDividendIncome)
            print ('Movers:', movers)

            print ('Inserting ', symbol, ' in HOLDINGS table')
            print ('Check if input ticker', stock, 'exists in HOLDINGS table.')

            resp = holdingsTable.scan(
                FilterExpression = Attr('Symbol').eq(stock)
            )

            print ('resp:', resp)

            item = resp['Items']
            if len(item) > 0:
                print ('Ticker exists in HOLDINGS table, update the row for: ', item)
                itemResp = item[0]
                print ('itemResp:', itemResp)
                print ("itemResp['PositionID']:", itemResp['PositionID'])
                holdingsTable.update_item(
                    Key={
                        'PositionID': itemResp['PositionID']
                    },
                    UpdateExpression="SET Symbol=:val1,Shares=:val2,AvgPx=:val3,LastPrice=:val4,Currency=:val5,IVType=:val6,CompanyName=:val7,Sector=:val8,CostBasisUSD=:val9,MktValUSD=:val10,ProfitLossUSD=:val11,ProfitLossPct=:val12,DividendYield=:val13,AnnualDividend=:val14,AnnualDividendIncome=:val15,Movers=:val16",
                    ExpressionAttributeValues={
                        ':val1': symbol,
                        ':val2': Decimal(str(noOfShares)),
                        ':val3': Decimal(str(avgPx)),
                        ':val4': Decimal(str(lastPx)),
                        ':val5': curr,
                        ':val6': ivType,
                        ':val7': compName,
                        ':val8': sect,
                        ':val9': Decimal(str(costBasis)),
                        ':val10': Decimal(str(mktVal)),
                        ':val11': Decimal(str(profitOrLoss)),
                        ':val12': Decimal(str(profitOrLossPct)),
                        ':val13': Decimal(str(divYieldPct)),
                        ':val14': Decimal(str(annualDividend)),
                        ':val15': Decimal(str(annualDividendIncome)),
                        ':val16': Decimal(str(movers))
                    }
                )

            else:
                print ('New ticker, so add to HOLDINGS table')

                resp = holdingsTable.put_item(
                TableName='HOLDINGS',
                Item={
                        'PositionID' : str(uuid.uuid1()),
                        'Symbol' : symbol,
                        'Shares' : Decimal(str(noOfShares)),
                        'AvgPx' : Decimal(str(avgPx)),
                        'LastPrice' : Decimal(str(lastPx)),
                        'Currency' : curr,
                        'IVType' : ivType,
                        'CompanyName' : compName,
                        'Sector' : sect,
                        'CostBasisUSD' : Decimal(str(costBasis)),
                        'MktValUSD' : Decimal(str(mktVal)),
                        'ProfitLossUSD' : Decimal(str(profitOrLoss)),
                        'ProfitLossPct' : Decimal(str(profitOrLossPct)),
                        'DividendYield' : Decimal(str(divYieldPct)),
                        'AnnualDividend' : Decimal(str(annualDividend)),
                        'AnnualDividendIncome' : Decimal(str(annualDividendIncome)),
                        'Movers' : Decimal(str(movers))
                    }
                )

                print ('Resp:')
                print (resp)

            portfolioList.append([symbol,noOfShares,avgPx,ivType,curr,lastPx,compName,sect,costBasis,mktVal,profitOrLoss,profitOrLossPct,divYieldPct,annualDividend,annualDividendIncome,movers])
            portfolioDf = pd.DataFrame(portfolioList,columns=['Symbol','Shares','AvgPx', 'IVType','Currency','LastPrice','CompanyName','Sector','CostBasisUSD','MktValUSD','ProfitLossUSD','ProfitLossPct','DividendYield','AnnualDividend','AnnualDividendIncome','Movers'])

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
        tradesDf = pd.DataFrame(tradesDict, columns=['Side','Ticker','Date','IVType','Shares','Avg Px'])
        print (tradesDf)

        colList = ['Side','Ticker','Date','IVType','Shares','Avg Px']

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
        holdingsDf = pd.DataFrame(holdingsDict, columns=['Symbol','Shares','AvgPx','IVType','Currency','LastPrice','CompanyName','Sector','CostBasisUSD','MktValUSD','ProfitLossUSD','ProfitLossPct','DividendYield','AnnualDividend','AnnualDividendIncome','Movers'])
        print (holdingsDf)
        
        colList = ['Symbol','Shares','AvgPx','IVType','Currency','LastPrice','CompanyName','Sector','CostBasisUSD','MktValUSD','ProfitLossUSD','ProfitLossPct','DividendYield','AnnualDividend','AnnualDividendIncome','Movers']

        for j in range(0,holdingsDf.shape[1]):
            self.entry = tk.Entry(self.frame_right, width=10,bg='lightblue',justify='center')
            self.entry.grid(row=0, column=j)
            self.entry.insert(tk.END, colList[j])

        # An approach for creating the table
        for i in range(0, holdingsDf.shape[0]):
            for j in range(0, holdingsDf.shape[1]):
       
                self.entry = tk.Entry(self.frame_right, width=10)
                self.entry.grid(row=i+1, column=j)

                if holdingsDf.columns[j] is None:
                    holdingsDf.columns[j] = 'NA'

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
