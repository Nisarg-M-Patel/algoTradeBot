import json
import requests
import pandas as pd
import datetime
from validInput import get_valid_date_range

market_symbol = "btcusd"
url = f"https://www.bitstamp.net/api/v2/ohlc/{market_symbol}/"

"""need step and limit for parameters"""

"""start date and time"""
start, end  = get_valid_date_range()
#start = "2023-12-01"
#end = "2023-12-02"

"""generate a range of dates and convert to epoch"""
dates = pd.date_range(start=start, end=end, freq="1H")
dates = [int(x.value / 10**9) for x in list(dates)]

master_data = []
for first, last in zip(dates, dates[1:]):
    print(first,last)
    params = {
        "step" : 60,
        "limit" : 1000,
        "start" : first,
        "end" : last
    }

    data = requests.get(url= url, params= params)

    """list of ohlc candlesticks"""
    data = data.json()["data"]["ohlc"]

    master_data += data

df = pd.DataFrame(master_data)
df = df.drop_duplicates()
df["timestamp"] = df["timestamp"].astype(int)
df = df.sort_values(by="timestamp")
df = df [df["timestamp"] >= dates[0]]
df = df [df["timestamp"] < dates[-1]]
print(df)
df.to_csv("tutorial.csv", index=False)
