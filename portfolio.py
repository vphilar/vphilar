import tkinter as tk
from tkinter import Scrollbar, messagebox, ttk
from webbrowser import BackgroundBrowser
import boto
import customtkinter
from matplotlib import ticker 
import pandas as pd
from requests import post
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
import datetime as dt



class App(customtkinter.CTk):

    screen_width = 600
    screen_height = 600

    def __init__(self):
        super().__init__()

        self.window_width = self.screen_width * 3
        self.window_height = self.screen_height * 2

        self.window_start_x = (self.screen_width)
        self.window_start_y = (self.screen_height)

        self.title("My Portfolio")
        self.geometry('1500x700')
        #self.geometry("%dx%d+%d+%d" % (self.window_width, self.window_height, self.window_start_x, self.window_start_y))
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

        """self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Add New Trade",
                                                command=self.AddNewTrade)
        self.button_1.grid(row=2, column=0, pady=10, padx=20)"""

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Trades",
                                                command=self.ShowAllTrades)
        self.button_1.grid(row=5, column=0, pady=10, padx=20)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Holdings",
                                                command=self.CurrentHoldings)
        self.button_1.grid(row=7, column=0, pady=10, padx=20)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Annual Income",
                                                command=self.AnnualIncomeCalculation)
        self.button_1.grid(row=9, column=0, pady=10, padx=20)

        self.label_mode = customtkinter.CTkLabel(master=self.frame_left, text="Appearance Mode:")
        self.label_mode.grid(row=15, column=0, pady=0, padx=20, sticky="w")

        self.optionmenu_1 = customtkinter.CTkOptionMenu(master=self.frame_left,
                                                        values=["Light", "Dark", "System"],
                                                        command=self.change_appearance_mode)
        self.optionmenu_1.grid(row=16, column=0, pady=10, padx=20, sticky="w")

    """def AddNewTrade(self):
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
        self.AddButton.grid(row=1, column=11, pady=10, padx=20)"""


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
        inputTkr = self.tkr.get()
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
            if inputTkr == finalTradesDf.loc[idx, 'Ticker']: 
                print ('Found match - ', inputTkr)

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
                            ':val2': Decimal(str(round(noOfShares,3))),
                            ':val3': Decimal(str(round(avgPx,3))),
                            ':val4': Decimal(str(round(lastPx,3))),
                            ':val5': curr,
                            ':val6': ivType,
                            ':val7': compName,
                            ':val8': sect,
                            ':val9': Decimal(str(round(costBasis,3))),
                            ':val10': Decimal(str(round(mktVal,3))),
                            ':val11': Decimal(str(round(profitOrLoss,3))),
                            ':val12': Decimal(str(round(profitOrLossPct,3))),
                            ':val13': Decimal(str(round(divYieldPct,3))),
                            ':val14': Decimal(str(round(annualDividend,3))),
                            ':val15': Decimal(str(round(annualDividendIncome,3))),
                            ':val16': Decimal(str(round(movers,3)))
                        }
                    )

                else:
                    print ('New ticker, so add to HOLDINGS table')

                    resp = holdingsTable.put_item(
                    TableName='HOLDINGS',
                    Item={
                            'PositionID' : str(uuid.uuid1()),
                            'Symbol' : symbol,
                            'Shares' : Decimal(str(round(noOfShares,3))),
                            'AvgPx' : Decimal(str(round(avgPx,3))),
                            'LastPrice' : Decimal(str(round(lastPx,3))),
                            'Currency' : curr,
                            'IVType' : ivType,
                            'CompanyName' : compName,
                            'Sector' : sect,
                            'CostBasisUSD' : Decimal(str(round(costBasis,3))),
                            'MktValUSD' : Decimal(str(round(mktVal,3))),
                            'ProfitLossUSD' : Decimal(str(round(profitOrLoss,3))),
                            'ProfitLossPct' : Decimal(str(round(profitOrLossPct,3))),
                            'DividendYield' : Decimal(str(round(divYieldPct,3))),
                            'AnnualDividend' : Decimal(str(round(annualDividend,3))),
                            'AnnualDividendIncome' : Decimal(str(round(annualDividendIncome,3))),
                            'Movers' : Decimal(str(round(movers,3)))
                        }
                    )

                    print ('Resp:')
                    print (resp)

                portfolioList.append([symbol,noOfShares,avgPx,ivType,curr,lastPx,compName,sect,costBasis,mktVal,profitOrLoss,profitOrLossPct,divYieldPct,annualDividend,annualDividendIncome,movers])
                portfolioDf = pd.DataFrame(portfolioList,columns=['Symbol','Shares','AvgPx', 'IVType','Currency','LastPrice','CompanyName','Sector','CostBasisUSD','MktValUSD','ProfitLossUSD','ProfitLossPct','DividendYield','AnnualDividend','AnnualDividendIncome','Movers'])

                print (portfolioDf)

                messagebox.showinfo('Success!', 'HOLDINGS updated!')
                print ('HOLDINGS updated!')
                
            else:
                print ('Skip this ticker, no processing required - ', inputTkr)

        self.ShowAllTrades()


    def callback(self, eventObject):
        print ('Got in here!')
        abc = eventObject.widget.get()
        ctry = self.tickerCntry.get()
        print ('ctry:', ctry)
        tkrList = [item for item in list(self.stockListDf[ctry]) if not(pd.isnull(item)) == True]
        self.tkr.config(value=tkrList)



    
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

        self.frame_right_upper_input = customtkinter.CTkFrame(master=self.frame_right, highlightbackground="blue", highlightthickness=2)
        self.frame_right_upper_input.grid(sticky="NEWS", padx=20, pady=20)
        
        self.frame_right_lower_input = customtkinter.CTkFrame(master=self.frame_right, highlightbackground="blue", highlightthickness=2)
        self.frame_right_lower_input.grid(sticky="NEWS", padx=20, pady=20)
 
        #Add some style
        style = ttk.Style()

        #Pick a theme
        style.theme_use("default")
        style.configure("Treeview",background="white", foreground="black", rowheight=25, fieldbackground="white")
        style.map("Treeview", background=[('selected', 'blue')])

        #Create Treeview
        self.my_tree = ttk.Treeview(self.frame_right_upper_input)
        self.my_tree['columns'] = ('Side', 'Ticker', 'Date', 'IVType', 'Shares','Avg Px')

        self.my_tree.column('#0', width=120, minwidth=25, stretch=tk.YES)
        self.my_tree.column('Side', anchor=tk.CENTER, width=120)
        self.my_tree.column('Ticker', anchor=tk.CENTER, width=120)
        self.my_tree.column('Date', anchor=tk.CENTER, width=120)
        self.my_tree.column('IVType', anchor=tk.CENTER, width=120)
        self.my_tree.column('Shares', anchor=tk.CENTER, width=120)
        self.my_tree.column('Avg Px', anchor=tk.CENTER, width=120)

        self.my_tree.heading('#0', text="Label", anchor=tk.CENTER)
        self.my_tree.heading('Side', text='Side', anchor=tk.CENTER)
        self.my_tree.heading('Ticker', text='Ticker', anchor=tk.CENTER)
        self.my_tree.heading('Date', text='Date', anchor=tk.CENTER)
        self.my_tree.heading('IVType', text='IVType', anchor=tk.CENTER)
        self.my_tree.heading('Shares', text='Shares', anchor=tk.CENTER)
        self.my_tree.heading('Avg Px', text='Avg Px', anchor=tk.CENTER)

        #Create stripped row tags
        self.my_tree.tag_configure('oddrow', background='white')
        self.my_tree.tag_configure('evenrow', background='lightblue')

        global count
        count = 0 

        tradesDf['Date'] = pd.to_datetime(tradesDf['Date'])
        tradesDf['Date'] = tradesDf['Date'].apply(lambda x: str(x).split(' ')[0])
        print ('Sorted tradesDf:', tradesDf)
        tradesDf = tradesDf.sort_values('Date', ascending=False)
        
        for _, row in tradesDf.iterrows():

            if count % 2 == 0:
                self.my_tree.insert(parent='', index='end', iid=count, text='Parent', values=(row['Side'],row['Ticker'],row['Date'],row['IVType'],row['Shares'],row['Avg Px']), tags='evenrow')
            else:
                self.my_tree.insert(parent='', index='end', iid=count, text='Parent', values=(row['Side'],row['Ticker'],row['Date'],row['IVType'],row['Shares'],row['Avg Px']), tags='oddrow')

            count += 1

        self.my_tree.grid(row=0, column=0)

        self.lower_heading = customtkinter.CTkLabel(self.frame_right_lower_input, text='ENTER NEW TRADE', text_color='#ffd921', fg_color='#006666')
        self.lower_heading.grid(row=1, column=7, sticky="N", padx=10, pady=10)

        #Labels
        self.sideLabel = customtkinter.CTkLabel(self.frame_right_lower_input, text='Side')
        self.sideLabel.grid(row=2, column=3, sticky="W", padx=10, pady=10)

        self.tkrLabel = customtkinter.CTkLabel(self.frame_right_lower_input, text='Country')
        self.tkrLabel.grid(row=2, column=5, sticky="W", padx=10, pady=10)

        self.tkrLabel = customtkinter.CTkLabel(self.frame_right_lower_input, text='Ticker')
        self.tkrLabel.grid(row=2, column=7, sticky="W", padx=10, pady=10)

        self.dateLabel = customtkinter.CTkLabel(self.frame_right_lower_input, text='Date')
        self.dateLabel.grid(row=2, column=9, sticky="W", padx=10, pady=10)

        self.sharesLabel = customtkinter.CTkLabel(self.frame_right_lower_input, text='Shares')
        self.sharesLabel.grid(row=2, column=11, sticky="W", padx=10, pady=10)

        self.avgPxLabel = customtkinter.CTkLabel(self.frame_right_lower_input, text='Avg Px')
        self.avgPxLabel.grid(row=2, column=13, sticky="W", padx=10, pady=10)

        #Entry Box
        self.sideComboBox = customtkinter.CTkComboBox(master=self.frame_right_lower_input,
                                                    values=["Buy", "Sell"])
        self.sideComboBox.grid(row=4, column=3, sticky="W", padx=10, pady=10)

        self.stockListDf = pd.read_csv('/Users/vikramphilar/Desktop/stocklist.csv')
        self.stockListDf = self.stockListDf.T
        cols = self.stockListDf.iloc[0]
        self.stockListDf = self.stockListDf[1:]
        self.stockListDf.columns = cols
        print (self.stockListDf.head(5))

        self.tickerCntry = customtkinter.CTkComboBox(master=self.frame_right_lower_input,
                                                    values=list(self.stockListDf.columns))
        self.tickerCntry.grid(row=4, column=5, sticky="W", padx=10, pady=10)
        
        self.tkr = ttk.Combobox(master=self.frame_right_lower_input)
        self.tkr.grid(row=4, column=7, sticky="W", padx=10, pady=10)
        self.tkr.bind('<Button-1>', self.callback)

        self.cal = tkc.DateEntry(master=self.frame_right_lower_input,
                                            width=12,
                                            borderwidth=2,
                                            foreground="black",
                                            placeholder_text="Date")
        self.cal.grid(row=4, column=9, sticky="W", padx=10, pady=10)

        self.shares = customtkinter.CTkEntry(self.frame_right_lower_input)
        self.shares.grid(row=4, column=11, sticky="W", padx=10, pady=10)

        self.avgPx = customtkinter.CTkEntry(self.frame_right_lower_input)
        self.avgPx.grid(row=4, column=13, sticky="W", padx=10, pady=10)

        #Buttons
        self.addNewTradeButton = customtkinter.CTkButton(self.frame_right_lower_input, text='Add New Trade', command=self.AddTradeToDB)
        self.addNewTradeButton.grid(row=6, column=3, sticky="W", padx=10, pady=10)

        self.addRefreshButton = customtkinter.CTkButton(self.frame_right_lower_input, text='Refresh', command=self.ShowAllTrades)
        self.addRefreshButton.grid(row=6, column=5, sticky="W", padx=10, pady=10)

        #Remove all trades
        self.removeAllButton = customtkinter.CTkButton(self.frame_right_lower_input, text='Remove All Trades', command=self.RemoveAllTrades)
        self.removeAllButton.grid(row=6, column=7, sticky="W", padx=10, pady=10)

        #Remove one trade
        self.removeOneButton = customtkinter.CTkButton(self.frame_right_lower_input, text='Remove One Selected', command=self.RemoveOneTrade)
        self.removeOneButton.grid(row=6, column=9, sticky="W", padx=10, pady=10)

        #Remove multiple trades
        self.removeMultiButton = customtkinter.CTkButton(self.frame_right_lower_input, text='Remove All Selected', command=self.RemoveAllSelected)
        self.removeMultiButton.grid(row=6, column=11, sticky="W", padx=10, pady=10)

        
    #Remove All trades
    def RemoveAllTrades(self):
        print ('Removing all trades')
        for row in self.my_tree.get_children():
            self.my_tree.delete(row)

        #Add code here to delete all trades from the TRADES table and update HOLDINGS table in DynamoDB

    #Remove One Trade
    def RemoveOneTrade(self):
        print ('Remove one selected')
        selRow = self.my_tree.selection()[0]
        self.my_tree.delete(selRow)

        #Add code here to delete the selected trade from TRADES table and update HOLDINGS for that stock in DynamoDB

    #Remove All Selected Trades
    def RemoveAllSelected(self):
        print ('Remove all selected')
        selRows = self.my_tree.selection()

        for row in selRows:
            self.my_tree.delete(row)

        #Add code here to delete the selected trades from TRADES table and update HOLDINGS for those stocks in DynamoDB




    """def AddRecord(self):
        global count
        self.my_tree.insert(parent='', index='end', iid=count, text='Parent', values=(self.sideComboBox.get(),self.ticker.get(),self.cal.get(),self.shares.get(),self.avgPx.get()))
        count += 1

        self.AddTradeToDB()

        #Clear the boxes
        self.sideComboBox.set('')
        self.ticker.delete(0, tk.END)
        self.cal.delete(0, tk.END)
        self.shares.delete(0, tk.END)
        self.avgPx.delete(0, tk.END)"""
        

    def CurrentHoldings(self):
        print("Get Current Holdings")

        for widget in self.frame_right.winfo_children():
            widget.destroy()

        self.frame_right_upper_input = customtkinter.CTkFrame(master=self.frame_right, highlightbackground="blue", highlightthickness=2)
        self.frame_right_upper_input.grid(sticky="NEWS", padx=20, pady=20)

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

        #Add some style
        style = ttk.Style()

        #Pick a theme
        style.theme_use("default")
        style.configure("Treeview",background="white", foreground="black", rowheight=25, fieldbackground="white")
        style.map("Treeview", background=[('selected', 'blue')])


        self.my_tree = ttk.Treeview(self.frame_right_upper_input)
        self.my_tree['columns'] = ('Symbol','Shares','AvgPx','IVType','Currency','LastPrice','CompanyName','Sector','CostBasisUSD','MktValUSD','ProfitLossUSD','ProfitLossPct','DividendYield','AnnualDividend','AnnualDividendIncome','Movers')

        self.my_tree.column('#0', width=75, minwidth=25, stretch=tk.YES)
        self.my_tree.column('Symbol', anchor=tk.CENTER, width=90, stretch=tk.YES)
        self.my_tree.column('Shares', anchor=tk.CENTER, width=90, stretch=tk.YES)
        self.my_tree.column('AvgPx', anchor=tk.CENTER, width=90, stretch=tk.YES)
        self.my_tree.column('IVType', anchor=tk.CENTER, width=90, stretch=tk.YES)
        self.my_tree.column('Currency', anchor=tk.CENTER, width=90, stretch=tk.YES)
        self.my_tree.column('LastPrice', anchor=tk.CENTER, width=90, stretch=tk.YES)
        self.my_tree.column('CompanyName', anchor=tk.CENTER, width=90, stretch=tk.YES)
        self.my_tree.column('Sector', anchor=tk.CENTER, width=90, stretch=tk.YES)
        self.my_tree.column('CostBasisUSD', anchor=tk.CENTER, width=90, stretch=tk.YES)
        self.my_tree.column('MktValUSD', anchor=tk.CENTER, width=90, stretch=tk.YES)
        self.my_tree.column('ProfitLossUSD', anchor=tk.CENTER, width=90, stretch=tk.YES)
        self.my_tree.column('ProfitLossPct', anchor=tk.CENTER, width=90, stretch=tk.YES)
        self.my_tree.column('DividendYield', anchor=tk.CENTER, width=90, stretch=tk.YES)
        self.my_tree.column('AnnualDividend', anchor=tk.CENTER, width=90, stretch=tk.YES)
        self.my_tree.column('AnnualDividendIncome', anchor=tk.CENTER, width=90, stretch=tk.YES)
        self.my_tree.column('Movers', anchor=tk.CENTER, width=90, stretch=tk.YES)

        self.my_tree.heading('#0', text="Label", anchor=tk.CENTER)
        self.my_tree.heading('Symbol', text='Symbol', anchor=tk.CENTER)
        self.my_tree.heading('Shares', text='Shares', anchor=tk.CENTER)
        self.my_tree.heading('AvgPx', text='AvgPx', anchor=tk.CENTER)
        self.my_tree.heading('IVType', text='IVType', anchor=tk.CENTER)
        self.my_tree.heading('Currency', text='Currency', anchor=tk.CENTER)
        self.my_tree.heading('LastPrice', text='LastPrice', anchor=tk.CENTER)
        self.my_tree.heading('CompanyName', text='CompanyName', anchor=tk.CENTER)
        self.my_tree.heading('Sector', text='Sector', anchor=tk.CENTER)
        self.my_tree.heading('CostBasisUSD', text='CostBasisUSD', anchor=tk.CENTER)
        self.my_tree.heading('MktValUSD', text='MktValUSD', anchor=tk.CENTER)
        self.my_tree.heading('ProfitLossUSD', text='ProfitLossUSD', anchor=tk.CENTER)
        self.my_tree.heading('ProfitLossPct', text='ProfitLossPct', anchor=tk.CENTER)
        self.my_tree.heading('DividendYield', text='DividendYield', anchor=tk.CENTER)
        self.my_tree.heading('AnnualDividend', text='AnnualDividend', anchor=tk.CENTER)
        self.my_tree.heading('AnnualDividendIncome', text='AnnualDividendIncome', anchor=tk.CENTER)
        self.my_tree.heading('Movers', text='Movers', anchor=tk.CENTER)


        #Create stripped row tags
        self.my_tree.tag_configure('oddrow', background='white')
        self.my_tree.tag_configure('evenrow', background='lightblue')

        cnt = 0 
        for _, row in holdingsDf.iterrows():
            if cnt % 2 == 0:
                self.my_tree.insert(parent='', index='end', iid=cnt, text='Parent', values=(row['Symbol'],row['Shares'],row['AvgPx'],row['IVType'],row['Currency'],row['LastPrice'],row['CompanyName'],row['Sector'],row['CostBasisUSD'],row['MktValUSD'],row['ProfitLossUSD'],row['ProfitLossPct'],row['DividendYield'],row['AnnualDividend'],row['AnnualDividendIncome'],row['Movers']), tags='evenrow')
            else:
                self.my_tree.insert(parent='', index='end', iid=cnt, text='Parent', values=(row['Symbol'],row['Shares'],row['AvgPx'],row['IVType'],row['Currency'],row['LastPrice'],row['CompanyName'],row['Sector'],row['CostBasisUSD'],row['MktValUSD'],row['ProfitLossUSD'],row['ProfitLossPct'],row['DividendYield'],row['AnnualDividend'],row['AnnualDividendIncome'],row['Movers']), tags='oddrow')
            
            cnt += 1

        self.my_tree.grid(row=0, column=0, sticky='NEWS')


    def AnnualIncomeCalculation(self):
        print ('Calculating Annual Income...')

        for widget in self.frame_right.winfo_children():
            widget.destroy()

        self.frame_one = customtkinter.CTkFrame(master=self.frame_right, highlightbackground="blue", highlightthickness=2)
        self.frame_one.grid(sticky="NEWS", padx=10, pady=10)
        
        self.frame_two = customtkinter.CTkFrame(master=self.frame_right, highlightbackground="blue", highlightthickness=2)
        self.frame_two.grid(sticky="NEWS", padx=10, pady=10)

        self.frame_three = customtkinter.CTkFrame(master=self.frame_right, highlightbackground="blue", highlightthickness=2)
        self.frame_three.grid(sticky="NEWS", padx=10, pady=10)
        
        self.frame_four = customtkinter.CTkFrame(master=self.frame_right, highlightbackground="blue", highlightthickness=2)
        self.frame_four.grid(sticky="NEWS", padx=10, pady=10)

        self.frame_five = customtkinter.CTkFrame(master=self.frame_right, highlightbackground="blue", highlightthickness=2)
        self.frame_five.grid(sticky="NEWS", padx=10, pady=10)

        self.frame_six = customtkinter.CTkFrame(master=self.frame_right, highlightbackground="blue", highlightthickness=2)
        self.frame_six.grid(sticky="NEWS", padx=10, pady=10)

        #DIVIDEND PAYMENTS HISTORY
        self.divPaymentsHistory = customtkinter.CTkLabel(self.frame_one, text='DIVIDEND\n\nPAYMENTS\n\nHISTORY', text_color='#ffd921', fg_color='#006666')
        self.divPaymentsHistory.grid(row=1, column=0, sticky="NEWS", padx=10, pady=10)

        #Buttons
        self.refreshButton = customtkinter.CTkButton(self.frame_one, text='Refresh', command=self.RefreshDividends)
        self.refreshButton.grid(row=2, column=0, sticky="W", padx=10, pady=10)

        #DIVIDEND LOGS
        self.heading = customtkinter.CTkLabel(self.frame_two, text='INPUT DIVIDENDS', text_color='#ffd921', fg_color='#006666')
        self.heading.grid(row=1, column=3, sticky="NEWS", padx=10, pady=10)

        #Labels
        self.sideLabel = customtkinter.CTkLabel(self.frame_two, text='Pay Date')
        self.sideLabel.grid(row=2, column=0, sticky="W", padx=5, pady=5)

        self.tkrLabel = customtkinter.CTkLabel(self.frame_two, text='Stock')
        self.tkrLabel.grid(row=2, column=2, sticky="W", padx=5, pady=5)

        self.dateLabel = customtkinter.CTkLabel(self.frame_two, text='Pre-Tax Amount')
        self.dateLabel.grid(row=2, column=3, sticky="W", padx=5, pady=5)

        self.sharesLabel = customtkinter.CTkLabel(self.frame_two, text='Post-Tax Amount')
        self.sharesLabel.grid(row=2, column=4, sticky="W", padx=5, pady=5)

        #Entry Box
        self.cal = tkc.DateEntry(master=self.frame_two,
                                            width=12,
                                            borderwidth=2,
                                            foreground="black",
                                            placeholder_text="Date")
        self.cal.grid(row=3, column=0, sticky="W", padx=10, pady=10)

        holdRes = boto3.resource('dynamodb')
        table = holdRes.Table('HOLDINGS')

        response = table.scan()
        holdingsDict = response['Items']
    
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            holdingsDict.extend(response['Items'])
        
        print (holdingsDict)

        print ('Current Holdings:')
        holdingsDf = pd.DataFrame(holdingsDict, columns=['Symbol','Shares','AvgPx','IVType','Currency','LastPrice','CompanyName','Sector','CostBasisUSD','MktValUSD','ProfitLossUSD','ProfitLossPct','DividendYield','AnnualDividend','AnnualDividendIncome','Movers'])
        print (holdingsDf)


        self.symbol = customtkinter.CTkComboBox(master=self.frame_two,
                                                    values=holdingsDf['Symbol'].tolist())
        self.symbol.grid(row=3, column=2, sticky="W", padx=10, pady=10)

        self.preTaxAmt = customtkinter.CTkEntry(self.frame_two)
        self.preTaxAmt.grid(row=3, column=3, sticky="W", padx=10, pady=10)

        self.postTaxAmt = customtkinter.CTkEntry(self.frame_two)
        self.postTaxAmt.grid(row=3, column=4, sticky="W", padx=10, pady=10)

        #Buttons
        self.addNewDivPaymentButton = customtkinter.CTkButton(self.frame_two, text='Add', command=self.AddDividendPayment)
        self.addNewDivPaymentButton.grid(row=3, column=6, sticky="W", padx=10, pady=10)


        self.yearlyPayments = customtkinter.CTkLabel(self.frame_three, text='YEARLY PAYMENTS', text_color='#ffd921', fg_color='#006666')
        self.yearlyPayments.grid(row=1, column=0, sticky="NEWS", padx=10, pady=10)

        #Buttons
        self.refreshButton = customtkinter.CTkButton(self.frame_three, text='Refresh', command=self.RefreshYearlyPayments)
        self.refreshButton.grid(row=2, column=0, sticky="W", padx=10, pady=10)

        self.mQYPayments = customtkinter.CTkLabel(self.frame_four, text='PAYMENTS BY MONTH, QUARTER & YEAR', text_color='#ffd921', fg_color='#006666')
        self.mQYPayments.grid(sticky="NEWS", padx=10, pady=10)

        self.totDivPerStock = customtkinter.CTkLabel(self.frame_five, text='TOTAL DIVIDENDS EARNED PER STOCK', text_color='#ffd921', fg_color='#006666')
        self.totDivPerStock.grid(sticky="NEWS", padx=10, pady=10)

        self.incBySector = customtkinter.CTkLabel(self.frame_six, text='ANNUAL INCOME BY SECTOR', text_color='#ffd921', fg_color='#006666')
        self.incBySector.grid(sticky="NEWS", padx=10, pady=10)


    def RefreshYearlyPayments(self):
        print ('Refresh Yearly Payments')

        tableExists = self.CheckIfTableExists('YEARLY_DIVIDENDS')

        if tableExists:
            yrlyDividendRes = boto3.resource('dynamodb')
            yrlyDividendsTable = yrlyDividendRes.Table('YEARLY_DIVIDENDS')
        else:
            # Create the DynamoDB table.
            yrlyDividendRes = boto3.resource('dynamodb')
            yrlyDividendsTable = yrlyDividendRes.create_table(
                TableName='YEARLY_DIVIDENDS',
                BillingMode='PROVISIONED',
                KeySchema=[
                    {   
                        'AttributeName': 'YearlyDivID',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'YearlyDivID',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
        
        yrlyDividendsTable.wait_until_exists()

        resp = yrlyDividendsTable.scan()
        yrlyDividendsDict = resp['Items']
    
        while 'LastEvaluatedKey' in resp:
            resp = yrlyDividendsTable.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
            yrlyDividendsDict.extend(resp['Items'])
        
        print (yrlyDividendsDict)

        print ('Dividends History:')
        yrlyDividendsDf = pd.DataFrame(yrlyDividendsDict, columns=['Year','Amount'])
        print (yrlyDividendsDf)    

        #Create Treeview
        self.my_yrly_div_tree = ttk.Treeview(self.frame_three)
        self.my_yrly_div_tree['columns'] = ('Year', 'Amount')

        self.my_yrly_div_tree.column('#0', width=120, minwidth=25, stretch=tk.YES)
        self.my_yrly_div_tree.column('Year', anchor=tk.CENTER, width=120)
        self.my_yrly_div_tree.column('Amount', anchor=tk.CENTER, width=120)

        self.my_yrly_div_tree.heading('#0', text="Label", anchor=tk.CENTER)
        self.my_yrly_div_tree.heading('Year', text='Year', anchor=tk.CENTER)
        self.my_yrly_div_tree.heading('Amount', text='Amount', anchor=tk.CENTER)

        #Create stripped row tags
        self.my_yrly_div_tree.tag_configure('oddrow', background='white')
        self.my_yrly_div_tree.tag_configure('evenrow', background='lightblue')

        global count
        count = 0 
        for _, row in yrlyDividendsDf.iterrows():

            if count % 2 == 0:
                self.my_yrly_div_tree.insert(parent='', index='end', iid=count, text='Parent', values=(row['Year'],row['Amount']), tags='evenrow')
            else:
                self.my_yrly_div_tree.insert(parent='', index='end', iid=count, text='Parent', values=(row['Year'],row['Amount']), tags='oddrow')

            count += 1

        self.my_yrly_div_tree.grid(row=1, column=1, sticky="NEWS")





    def RefreshDividends(self):
        print ('Refreshing dividends')

        tableExists = self.CheckIfTableExists('DIVIDENDS')

        if tableExists:
            dividendRes = boto3.resource('dynamodb')
            dividendsTable = dividendRes.Table('DIVIDENDS')
        else:
            # Create the DynamoDB table.
            dividendRes = boto3.resource('dynamodb')
            dividendsTable = dividendRes.create_table(
                TableName='DIVIDENDS',
                BillingMode='PROVISIONED',
                KeySchema=[
                    {   
                        'AttributeName': 'DivID',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'DivID',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
        
        dividendsTable.wait_until_exists()

        resp = dividendsTable.scan()
        dividendsDict = resp['Items']
    
        while 'LastEvaluatedKey' in resp:
            resp = dividendsTable.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
            dividendsDict.extend(resp['Items'])
        
        print (dividendsDict)

        print ('Dividends History:')
        dividendsDf = pd.DataFrame(dividendsDict, columns=['Date','Stock','PreTaxAmt','PostTaxAmt'])
        print (dividendsDf)       

        #Create Treeview
        self.my_ref_div_tree = ttk.Treeview(self.frame_one)
        self.my_ref_div_tree['columns'] = ('Date', 'Stock', 'PreTaxAmt', 'PostTaxAmt')

        self.my_ref_div_tree.column('#0', width=120, minwidth=25, stretch=tk.YES)
        self.my_ref_div_tree.column('Date', anchor=tk.CENTER, width=120)
        self.my_ref_div_tree.column('Stock', anchor=tk.CENTER, width=120)
        self.my_ref_div_tree.column('PreTaxAmt', anchor=tk.CENTER, width=120)
        self.my_ref_div_tree.column('PostTaxAmt', anchor=tk.CENTER, width=120)

        self.my_ref_div_tree.heading('#0', text="Label", anchor=tk.CENTER)
        self.my_ref_div_tree.heading('Date', text='Date', anchor=tk.CENTER)
        self.my_ref_div_tree.heading('Stock', text='Stock', anchor=tk.CENTER)
        self.my_ref_div_tree.heading('PreTaxAmt', text='PreTaxAmt', anchor=tk.CENTER)
        self.my_ref_div_tree.heading('PostTaxAmt', text='PostTaxAmt', anchor=tk.CENTER)

        #Create stripped row tags
        self.my_ref_div_tree.tag_configure('oddrow', background='white')
        self.my_ref_div_tree.tag_configure('evenrow', background='lightblue')

        global count
        count = 0 

        dividendsDf['Date'] = pd.to_datetime(dividendsDf['Date'])
        dividendsDf['Date'] = dividendsDf['Date'].apply(lambda x: str(x).split(' ')[0])
        print ('Sorted dividendsDf:', dividendsDf)
        dividendsDf = dividendsDf.sort_values('Date', ascending=False)
        for _, row in dividendsDf.iterrows():

            if count % 2 == 0:
                self.my_ref_div_tree.insert(parent='', index='end', iid=count, text='Parent', values=(row['Date'],row['Stock'],row['PreTaxAmt'],row['PostTaxAmt']), tags='evenrow')
            else:
                self.my_ref_div_tree.insert(parent='', index='end', iid=count, text='Parent', values=(row['Date'],row['Stock'],row['PreTaxAmt'],row['PostTaxAmt']), tags='oddrow')

            count += 1

        self.my_ref_div_tree.grid(row=1, column=1, sticky='NEWS')



    def CalcYearlyPayments(self, yrlyDividendsDf):

        print ('Calculating Yearly Payments')

        tableExists = self.CheckIfTableExists('YEARLY_DIVIDENDS')

        if tableExists:
            yrlyDividendRes = boto3.resource('dynamodb')
            yrlyDividendsTable = yrlyDividendRes.Table('YEARLY_DIVIDENDS')
        else:
            # Create the DynamoDB table.
            yrlyDividendRes = boto3.resource('dynamodb')
            yrlyDividendsTable = yrlyDividendRes.create_table(
                TableName='YEARLY_DIVIDENDS',
                BillingMode='PROVISIONED',
                KeySchema=[
                    {   
                        'AttributeName': 'YearlyDivID',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'YearlyDivID',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
        
        yrlyDividendsTable.wait_until_exists()

        print ('Dividends History:')
        yrlyDividendsDf['Date'] = yrlyDividendsDf['Date'].astype('datetime64')
        yrlyDividendsDf['Year'] = yrlyDividendsDf['Date'].dt.year
        yrlyDividendsDf['PostTaxAmt'] = yrlyDividendsDf['PostTaxAmt'].astype('float64')
        print (yrlyDividendsDf)    

        dividendsGrpDf = yrlyDividendsDf.groupby('Year')['PostTaxAmt'].sum().reset_index()
        print ('dividendsGrpDf:')
        print (dividendsGrpDf)


        #dividendsGrpDf = dividendsGrpDf.reset_index()
        print("Saving the following yearly dividends to DynamoDB:")
        print ('Year:', dividendsGrpDf['Year'])
        print ('Amount:', dividendsGrpDf['PostTaxAmt'])
        
        for idx, row in dividendsGrpDf.iterrows():

            print ('year:', dividendsGrpDf.loc[idx,'Year'])
            print ('Amt:', dividendsGrpDf.loc[idx,'PostTaxAmt'])
            yrlyDividendsTable.put_item(
                TableName='YEARLY_DIVIDENDS',
                Item={
                        'YearlyDivID' : str(uuid.uuid1()),
                        'Year' : str(dividendsGrpDf.loc[idx,'Year']),
                        'Amount' : str(dividendsGrpDf.loc[idx,'PostTaxAmt']),
                    }
                )

        messagebox.showinfo('Success!', 'Updated YEARLY_DIVIDENDS table!')
        print ('Item inserted in YEARLY_DIVIDENDS table!')

        resp = yrlyDividendsTable.scan()
        yrlyDividendsDict = resp['Items']
    
        while 'LastEvaluatedKey' in resp:
            resp = yrlyDividendsTable.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
            yrlyDividendsDict.extend(resp['Items'])
        
        print (yrlyDividendsDict)

        print ('Dividends History:')
        yrlyDividendsDf = pd.DataFrame(yrlyDividendsDict, columns=['Year','Amount'])
        print (yrlyDividendsDf)    

        #Create Treeview
        self.my_div_tree = ttk.Treeview(self.frame_three)
        self.my_div_tree['columns'] = ('Year', 'Amount')

        self.my_div_tree.column('#0', width=120, minwidth=25, stretch=tk.YES)
        self.my_div_tree.column('Year', anchor=tk.CENTER, width=120)
        self.my_div_tree.column('Amount', anchor=tk.CENTER, width=120)

        self.my_div_tree.heading('#0', text="Label", anchor=tk.CENTER)
        self.my_div_tree.heading('Year', text='Year', anchor=tk.CENTER)
        self.my_div_tree.heading('Amount', text='Amount', anchor=tk.CENTER)

        #Create stripped row tags
        self.my_div_tree.tag_configure('oddrow', background='white')
        self.my_div_tree.tag_configure('evenrow', background='lightblue')

        global count
        count = 0 

        yrlyDividendsDf = yrlyDividendsDf.sort_values('Year', ascending=False)
        for _, row in yrlyDividendsDf.iterrows():

            if count % 2 == 0:
                self.my_div_tree.insert(parent='', index='end', iid=count, text='Parent', values=(row['Year'],row['Amount']), tags='evenrow')
            else:
                self.my_div_tree.insert(parent='', index='end', iid=count, text='Parent', values=(row['Year'],row['Amount']), tags='oddrow')

            count += 1

        self.my_div_tree.grid(row=1, column=1, sticky="NEWS")

        #yrlyDividendsTable.delete()





    def AddDividendPayment(self):
        
        print ('Add dividend pay:')

        tableExists = self.CheckIfTableExists('DIVIDENDS')

        if tableExists:
            dividendRes = boto3.resource('dynamodb')
            dividendsTable = dividendRes.Table('DIVIDENDS')
        else:
            # Create the DynamoDB table.
            dividendRes = boto3.resource('dynamodb')
            dividendsTable = dividendRes.create_table(
                TableName='DIVIDENDS',
                BillingMode='PROVISIONED',
                KeySchema=[
                    {   
                        'AttributeName': 'DivID',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'DivID',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
        
        dividendsTable.wait_until_exists()

        print("Saving the following dividend to DynamoDB:")
        print ('Date:', self.cal.get())
        print ('Symbol:', self.symbol.get())
        print ('PreTaxAmt:', self.preTaxAmt.get())
        print ('PostTaxAmt:', self.postTaxAmt.get())
        
        if self.cal.get() != "" and self.symbol.get() != "" and self.preTaxAmt.get() != "" and self.postTaxAmt.get() != "":

            dividendsTable.put_item(
                TableName='DIVIDENDS',
                Item={
                        'DivID' : str(uuid.uuid1()),
                        'Date' : self.cal.get(),
                        'Stock' :  self.symbol.get(),
                        'PreTaxAmt' : Decimal(self.preTaxAmt.get()),
                        'PostTaxAmt' : Decimal(self.postTaxAmt.get())
                    }
                )

            messagebox.showinfo('Success!', 'Updated DIVIDENDS table!')
            print ('Item inserted in DIVIDENDS table!')

            resp = dividendsTable.scan()
            dividendsDict = resp['Items']
        
            while 'LastEvaluatedKey' in resp:
                resp = dividendsTable.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
                dividendsDict.extend(resp['Items'])
            
            print (dividendsDict)

            print ('Dividends History:')
            dividendsDf = pd.DataFrame(dividendsDict, columns=['Date','Stock','PreTaxAmt','PostTaxAmt'])
            print (dividendsDf)

            #Create Treeview
            self.my_div_pay_tree = ttk.Treeview(self.frame_one)
            self.my_div_pay_tree['columns'] = ('Date', 'Stock', 'PreTaxAmt', 'PostTaxAmt')

            self.my_div_pay_tree.column('#0', width=120, minwidth=25, stretch=tk.YES)
            self.my_div_pay_tree.column('Date', anchor=tk.CENTER, width=120)
            self.my_div_pay_tree.column('Stock', anchor=tk.CENTER, width=120)
            self.my_div_pay_tree.column('PreTaxAmt', anchor=tk.CENTER, width=120)
            self.my_div_pay_tree.column('PostTaxAmt', anchor=tk.CENTER, width=120)

            self.my_div_pay_tree.heading('#0', text="Label", anchor=tk.CENTER)
            self.my_div_pay_tree.heading('Date', text='Date', anchor=tk.CENTER)
            self.my_div_pay_tree.heading('Stock', text='Stock', anchor=tk.CENTER)
            self.my_div_pay_tree.heading('PreTaxAmt', text='PreTaxAmt', anchor=tk.CENTER)
            self.my_div_pay_tree.heading('PostTaxAmt', text='PostTaxAmt', anchor=tk.CENTER)

            #Create stripped row tags
            self.my_div_pay_tree.tag_configure('oddrow', background='white')
            self.my_div_pay_tree.tag_configure('evenrow', background='lightblue')

            global count
            count = 0 

            dividendsDf['Date'] = pd.to_datetime(dividendsDf['Date'])
            dividendsDf['Date'] = dividendsDf['Date'].apply(lambda x: str(x).split(' ')[0])
            print ('Sorted dividendsDf:', dividendsDf)
            dividendsDf = dividendsDf.sort_values('Date', ascending=False)

            for _, row in dividendsDf.iterrows():

                if count % 2 == 0:
                    self.my_div_pay_tree.insert(parent='', index='end', iid=count, text='Parent', values=(row['Date'],row['Stock'],row['PreTaxAmt'],row['PostTaxAmt']), tags='evenrow')
                else:
                    self.my_div_pay_tree.insert(parent='', index='end', iid=count, text='Parent', values=(row['Date'],row['Stock'],row['PreTaxAmt'],row['PostTaxAmt']), tags='oddrow')

                count += 1

            self.my_div_pay_tree.grid(row=1, column=1, sticky='NEWS')

            self.CalculateYearlyPayments(self.cal.get(), self.postTaxAmt.get())

        else:

            messagebox.showerror('Input Error', 'Please ensure date, ticker, pre-tax and post-tax amounts are filled in and click Add again.')    

        

    def CalculateYearlyPayments(self, inpDate, postTax):
        print ('Faster way to calculate yearly payments')

        tableExists = self.CheckIfTableExists('YEARLY_DIVIDENDS')

        if tableExists:
            yrlyDividendRes = boto3.resource('dynamodb')
            yrlyDividendsTable = yrlyDividendRes.Table('YEARLY_DIVIDENDS')
        else:
            # Create the DynamoDB table.
            yrlyDividendRes = boto3.resource('dynamodb')
            yrlyDividendsTable = yrlyDividendRes.create_table(
                TableName='YEARLY_DIVIDENDS',
                BillingMode='PROVISIONED',
                KeySchema=[
                    {   
                        'AttributeName': 'YearlyDivID',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'YearlyDivID',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
        
        yrlyDividendsTable.wait_until_exists()

        datem = dt.datetime.strptime(inpDate, "%m/%d/%y")
        print ('Year of the date Inputted', datem.year)

        resp = yrlyDividendsTable.scan(
            FilterExpression = Attr('Year').eq(datem.year)
        )

        print ('resp:', resp)

        item = resp['Items']
        if len(item) > 0:
            print ('Year exists in YEARLY_DIVIDENDS table, update the row for: ', datem.year)
            itemResp = item[0]
            print ('itemResp:', float(itemResp['Amount']) + float(postTax))
            print ("itemResp['YearlyDivID']:", itemResp['YearlyDivID'])
            yrlyDividendsTable.update_item(
                Key={
                    'YearlyDivID': itemResp['YearlyDivID']
                },
                UpdateExpression="SET Amount=:val1",
                ExpressionAttributeValues={
                    ':val1': Decimal(itemResp['Amount']) + Decimal(postTax)
                }
            )

        else:
            print ('New Year, so add to YEARLY_DIVIDENDS table')

            resp = yrlyDividendsTable.put_item(
            TableName='YEARLY_DIVIDENDS',
            Item={
                    'YearlyDivID' : str(uuid.uuid1()),
                    'Year' : datem.year,
                    'Amount' : Decimal(postTax)
                }
            )

            print ('Resp:')
            print (resp)

        yrlyDivList = []

        yrlyDivList.append([inpDate, postTax])
        yrDivDf = pd.DataFrame(yrlyDivList,columns=['Year','Amount'])

        print (yrDivDf)

        messagebox.showinfo('Success!', 'YEARLY_DIVIDENDS updated!')
        print ('YEARLY_DIVIDENDS updated!')

        self.RefreshYearlyPayments()


        




    def button_event(self):
        print("Button pressed")

    def change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def on_closing(self, event=0):
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
