import requests as req
from datetime import datetime
import dload
import csv
import os
import tkinter as tk
from tkinter import ttk
import tkcalendar as tkcal 

root = tk.Tk()
root.title("Volatility & OI Moniter")

style = ttk.Style()
style.configure("Treeview", font=('Britannic', 11, 'bold'), rowheight=25)
style.configure("Treeview.Heading", font=('Britannic' ,13, 'bold'))

# Tkinter Bug Work Around
if root.getvar('tk_patchLevel')=='8.6.9': #and OS_Name=='nt':
    def fixed_map(option):
        # Fix for setting text colour for Tkinter 8.6.9
        # From: https://core.tcl.tk/tk/info/509cafafae
        #
        # Returns the style map for 'option' with any styles starting with
        # ('!disabled', '!selected', ...) filtered out.
        #
        # style.map() returns an empty list for missing options, so this
        # should be future-safe.
        return [elm for elm in style.map('Treeview', query_opt=option) if elm[:2] != ('!disabled', '!selected')]
    style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))

frame_top = tk.Frame(root)
frame_top.pack(padx=5, pady=20)

tv = ttk.Treeview(
    frame_top, 
    columns=(1, 2, 3, 4), 
    show='headings', 
    height=10)
tv.pack()

tv.heading(1, text='Security')
tv.heading(2, text='Volatility')
tv.heading(3, text='OI')
tv.heading(4, text='Volume')

def delete_data_files(DATA_DIRECTORY):
    datafilelist = [ f for f in os.listdir(DATA_DIRECTORY) if not f == "stocks.txt"]
    for file in datafilelist:
        os.remove(os.path.join(DATA_DIRECTORY,file))

def calc():
    day = calender.get_date()
    day_str = day.strftime('%d%m%Y')

    #formatting for volume URL
    month = day.strftime('%b').upper()
    year = day.strftime('%Y')
    date_volume = day.strftime('%d%b%Y').upper()

    DATA_DIRECTORY = ".\\Data Files\\"
    OI_URL = f"https://www1.nseindia.com/archives/nsccl/mwpl/nseoi_{day_str}.zip"
    VOLATILITY_URL = f"https://www1.nseindia.com/archives/nsccl/volt/CMVOLT_{day_str}.CSV"
    VOLUME_URL = f"https://www1.nseindia.com/content/historical/EQUITIES/{year}/{month}/cm{date_volume}bhav.csv.zip"
    volume_zip_file = dload.save_unzip(VOLUME_URL, f"{DATA_DIRECTORY}", delete_after=True)
    OI_zip_file = dload.save_unzip(OI_URL, f"{DATA_DIRECTORY}", delete_after=True)



    data = req.get(VOLATILITY_URL)
    vol_file_name = f"VOLATILITY_{day_str}.csv"
    oi_file_name = f"nseoi_{day_str}.csv"
    volume_file_name = f"cm{date_volume}bhav.csv"
    FULL_PATH_VOLATILITY = os.path.join(DATA_DIRECTORY, vol_file_name)
    FULL_PATH_OI = os.path.join(DATA_DIRECTORY, oi_file_name)
    FULL_PATH_VOLUME = os.path.join(DATA_DIRECTORY, volume_file_name)
    with open(FULL_PATH_VOLATILITY, "wb") as f:
        f.write(data.content)

    with open("stocks.txt", "r") as f:
        nifty_50 = [stock.strip() for stock in f]

    nifty_50_data = {}

    with open(FULL_PATH_VOLATILITY) as f:
        csv_reader = csv.reader(f, delimiter=",")
        for row in csv_reader:
            if row[1] in nifty_50:
                nifty_50_data[row[1]] = [float(row[6])]

    with open(FULL_PATH_OI) as f:
        csv_reader = csv.reader(f, delimiter=",")
        for row in csv_reader:
            if row[3] in nifty_50:
                nifty_50_data[row[3]].append(int(row[5]))
    
    with open(FULL_PATH_VOLUME) as f:
        csv_reader = csv.reader(f, delimiter=",")
        for row in csv_reader:
            if row[0] in nifty_50:
                nifty_50_data[row[0]].append(int(row[8]))

    delete_data_files(".\\Data Files\\")
    return nifty_50_data

calender = tkcal.DateEntry(frame_top, selectmode="day")
calender.pack(pady=5)

row_lab = ttk.Label(frame_top, text="Show Rows:")
row_lab.pack()
row_entry_var = tk.StringVar(value="10")
row_entry = ttk.Entry(frame_top, textvariable=row_entry_var)
row_entry.pack(pady=5)

#print(nifty_50_data)

def set_table():
    for i in tv.get_children():
        tv.delete(i)
    nifty_50_data = calc()
    i = 0
    no_of_rows = int(row_entry_var.get())
    data_vol = sorted(nifty_50_data.items(), key=lambda x: x[1][2], reverse=True)[:no_of_rows]
    print(data_vol)
    sort_order = selected.get()
    if sort_order == "vol":
        sort_index = 0
    elif sort_order == "OI":
        sort_index = 1

    for k,v in sorted(data_vol, key=lambda x: x[1][sort_index], reverse=True):
        tv.insert(parent='', index=i, iid=i, values=(k, v[0], v[1], v[2]))
        i += 1


selected = tk.StringVar(value="OI")
r1 = ttk.Radiobutton(frame_top, text='Open Interest', value='OI', variable=selected, command=set_table)
r1.pack()
r2 = ttk.Radiobutton(frame_top, text='Volatility', value='vol', variable=selected, command=set_table)
r2.pack()

button = ttk.Button(frame_top, text="Search", command=set_table)
button.pack(pady=5)

root.mainloop()


