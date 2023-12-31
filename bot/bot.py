import pandas as pd
from decouple import config
from binance.client import Client
import pandas_ta as ta
import json
import os
import time
import datetime

client = Client(config("API_KEY"), config("SECRET_KEY"), testnet= True)
asset = "BTCUSDT"
balance = client.get_asset_balance(asset= "BTC")

def fetch_klines(asset):
    klines = client.get_historical_klines(asset, Client.KLINE_INTERVAL_1MINUTE,
                                          "1 hour ago UTC")
    """klines returns list of OHLCV values (Open time, Open, High, Low, Close, Volume,
      Close time, Quote asset volume, Number of trades, Taker buy base asset volume,
        Taker buy quote asset volume, Ignore)"""
    
    """trading on Close first as a test, reduce list to Open time, close"""
    klines = [[x[0], float(x[4])] for x in klines]
    klines = pd.DataFrame(klines, columns = ['time', 'price'])
    klines['time'] = pd.to_datetime(klines['time'],unit='ms')
    return klines

"""create an rsi column for each kline based on close"""
def get_rsi(asset):
    klines = fetch_klines(asset)
    klines["rsi"] = ta.rsi(close = klines["price"], length=14)
    """return final rsi"""
    return klines['rsi'].iloc[-1]

def create_account():
     account = {
         "is_buying":True,
         "assets":{},
     }
     with open("bot_account.json", "w") as F:
         F.write(json.dumps(account)) 

def log(msg):
    print(f"LOG: {msg}")
    if not os.path.isdir("logs"):
        os.mkdir("logs")
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    time = now.strftime("%H-%M-%S")
    
    with open(f"logs/{today}.txt", "a+") as log_file:
        log_file.write(f"{time} : {msg}\n")
    

log(asset)


"""initial rsi value"""
rsi = get_rsi("BTCUSDT")
old_rsi = rsi
entry = 0
exit = 0

while True:
    try:
        """check for existing acc"""
        if not os.path.exists("bot_account.json"):
            create_account()
        with open("bot_account.json") as f:
            account = json.load(f)
        old_rsi = rsi
        rsi = get_rsi(asset=asset)
        if account["is_buying"]:
            if rsi < entry and old_rsi > entry:
                #trade
                pass
            if rsi > exit and old_rsi < exit:
                #trade
                pass
        print(rsi)
        time.sleep(10)
    except:
        pass