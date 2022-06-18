from tkinter import *
import pandas as pd

# Table class
class Table:
    # Initialize a constructor
    def __init__(self, gui):

        # An approach for creating the table
        for i in range(total_rows):
            for j in range(total_columns):
                print(i)
                if i ==0:
                    self.entry = Entry(gui, width=20, bg='LightSteelBlue',fg='Black',
                                       font=('Arial', 16, 'bold'))
                else:
                    self.entry = Entry(gui, width=20, fg='blue',
                               font=('Arial', 16, ''))

                self.entry.grid(row=i, column=j)
                self.entry.insert(END, employee_df.values.tolist()[i][j])


# take the data
employee_list = [('ID', 'Name', 'City', 'Age'),
        (1, 'Gorge', 'California', 30),
       (2, 'Maria', 'New York', 19),
       (3, 'Albert', 'Berlin', 22),
       (4, 'Harry', 'Chicago', 19),
       (5, 'Vanessa', 'Boston', 31),
       (6, 'Ali', 'Karachi', 30)]

employee_df = pd.DataFrame(employee_list, columns = ['ID','Name','City','Age'])

# find total number of rows and
# columns in list
total_rows = len(employee_list)
total_columns = len(employee_list[0])

# create root window
gui = Tk()
table = Table(gui)
gui.mainloop()