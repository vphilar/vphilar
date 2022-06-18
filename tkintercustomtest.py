import tkinter as tk
import customtkinter 
import pandas as pd
import yfinance as yf
pd.set_option('max_columns', None)
pd.set_option("max_rows", None)
import boto3
from decimal import Decimal



class App(customtkinter.CTk):

    WIDTH = 780
    HEIGHT = 520

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
                                              text="PORTFOLIO:",
                                              text_font=("Roboto Medium", -16))  # font name and size in px
        self.label_1.grid(row=1, column=0, pady=10, padx=10)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Add New Trade",
                                                command=self.AddNewTrade)
        self.button_1.grid(row=2, column=0, pady=10, padx=20)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Current Holdings",
                                                command=self.CurrentHoldings)
        self.button_1.grid(row=3, column=0, pady=10, padx=20)


    def AddNewTrade(self):
        print("Adding a new trade")

        self.side = customtkinter.CTkEntry(master=self.frame_right,
                                            width=100,
                                            placeholder_text="Side")
        self.side.grid(row=1, column=0, columnspan=2, pady=20, padx=20, sticky="we")

        self.ticker = customtkinter.CTkEntry(master=self.frame_right,
                                            width=100,
                                            placeholder_text="Ticker")
        self.ticker.grid(row=2, column=0, columnspan=2, pady=20, padx=20, sticky="we")

        self.date = customtkinter.CTkEntry(master=self.frame_right,
                                            width=100,
                                            placeholder_text="Date")
        self.date.grid(row=3, column=0, columnspan=2, pady=20, padx=20, sticky="we")

        self.type = customtkinter.CTkEntry(master=self.frame_right,
                                            width=100,
                                            placeholder_text="Type")
        self.type.grid(row=4, column=0, columnspan=2, pady=20, padx=20, sticky="we")

        self.shares = customtkinter.CTkEntry(master=self.frame_right,
                                            width=100,
                                            placeholder_text="Shares")
        self.shares.grid(row=5, column=0, columnspan=2, pady=20, padx=20, sticky="we")

        self.avgPx = customtkinter.CTkEntry(master=self.frame_right,
                                            width=100,
                                            placeholder_text="Avg Price")
        self.avgPx.grid(row=6, column=0, columnspan=2, pady=20, padx=20, sticky="we")

        self.curr = customtkinter.CTkEntry(master=self.frame_right,
                                            width=100,
                                            placeholder_text="Currency")
        self.curr.grid(row=7, column=0, columnspan=2, pady=20, padx=20, sticky="we")

        self.AddButton = customtkinter.CTkButton(master=self.frame_right,
                                                text="Add Trade to DB",
                                                command=self.SaveTradeToDB)
        self.AddButton.grid(row=4, column=3, pady=10, padx=20)



    def SaveTradeToDB(self):
        print("Saving the following trade to DynamoDB:")
        print ('Side:', self.side.get())
        print ('Ticker:', self.ticker.get())
        print ('Date:', self.date.get())
        print ('Type:', self.type.get())
        print ('Shares:', self.shares.get())
        print ('Avg Price:', self.avgPx.get())
        print ('Currency:', self.curr.get())

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('TRADES')

        table.put_item(
        Item={
                'TradeID': str((table.item_count)+1),
                'Side': self.side.get(),
                'Ticker': self.ticker.get(),
                'Date': self.date.get(),
                'Type': self.type.get(),
                'Shares': Decimal(self.shares.get()),
                'Avg Px': Decimal(self.avgPx.get()),
                'Currency': self.curr.get()
            }
        )
        print ('Item inserted!')


    def CurrentHoldings(self):
        print("Get Current Holdings")


    def change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def on_closing(self, event=0):
        self.destroy()



if __name__ == "__main__":
    app = App()
    app.mainloop()
