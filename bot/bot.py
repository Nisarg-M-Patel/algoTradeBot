import pandas as pd
from decouple import config
from binance.client import Client
import pandas_ta as ta
import json
import os
import time
import datetime
import sys

client = Client(config("API_KEY"), config("SECRET_KEY"), testnet= True)
asset = "BTCUSDT"


def get_balance():
    balanceAsset = float(client.get_asset_balance(asset="BTC")['free'])
    balanceUSD = float(client.get_historical_klines(
    asset, Client.KLINE_INTERVAL_1MINUTE, limit=1)[0][4]) * balanceAsset
    balanceCash = float(client.get_asset_balance(asset='USDT')['free'])
    return [balanceAsset, balanceUSD, balanceCash]
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
     balance = get_balance()
     account = {
         "is_buying":True,
         "balance":[balance[0], balance[1], balance[2]]
     }
     with open("bot_account.json", "w") as F:
         F.write(json.dumps(account)) 

"""method to log messages to a file"""
def log(msg):
    print(f"LOG: {msg}")
    if not os.path.isdir("logs"):
        os.mkdir("logs")
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    time = now.strftime("%H-%M-%S")
    
    with open(f"logs/{today}.txt", "a+") as log_file:
        log_file.write(f"{time} : {msg}\n")
    
def do_trade(account, client, asset, side, quantity):
    
    if (side == "buy"):
        order = client.order_market_buy(
            symbol = asset,
            quantity = quantity
        )
        account['is_buying'] = False
        account['balance'] = get_balance()
    
    else:
        order = client.order_market_sell(
            symbol = asset,
            quantity = quantity
        )
        account['is_buying'] = True
        account['balance'] = client.get_balance()
    order_id = order["orderId"]
    while order["status"] != "FILLED":
        order = client.get_order(
           symbol = asset,
           orderId = order_id 
        )
        time.sleep(1) 
    price_paid = sum([float(fill["price"]) * float(fill["qty"]) for
                  fill in order["fills"]])
    print(order)
    log_trade(asset, side, price_paid, quantity)
    with open("bot_account.json", "w") as f:
        f.write(json.dumps(account))

def log_trade(sym, side, price, amount):
    log(f"{side} {amount} {sym} for {price}")
    
    if not os.path.isdir("trades"):
        os.mkdir("trades")

    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    time = now.strftime("%H-%M-%S")

    if not os.path.isfile(f"trades/{today}.csv"):
        with open(f"trades/{today}.csv", "w") as trade_file:
            trade_file.write("sym,side,amount,price\n")
    with open(f"trades/{today}.csv", "a+") as trade_file:
            trade_file.write(f"{sym},{side},{amount},{price}\n")

"""initial rsi value"""
rsi = get_rsi("BTCUSDT")
old_rsi = rsi
entry = 40
exit = 60

while True:
    try:
        """check for existing acc"""
        if not os.path.exists("bot_account.json"):
            create_account()
        with open("bot_account.json") as f:
            account = json.load(f)
        now = datetime.datetime.now()
        today = now.strftime("%Y-%m-%d")
        hms = now.strftime("%H:%M:%S")
        print(f"{today} {hms} is_buying:{account['is_buying']} / BTC:{account['balance'][0]} / BTCUSD:{account['balance'][1]} / USD:{account['balance'][2]}")
        #print(f"{today} {hms} {account}")
        old_rsi = rsi
        rsi = get_rsi(asset=asset)
        if account["is_buying"]:
            if rsi < entry and old_rsi > entry:
                do_trade(account, client, asset, "buy", "0.01")
            if rsi > exit and old_rsi < exit:
                do_trade(account, client, asset, "sell","0.01")
        print(f"RSI: {old_rsi} --> {rsi}\n\n")
        time.sleep(5)
    except Exception as exception:
        log("ERROR:  " + str(exception))
        sys.exit()