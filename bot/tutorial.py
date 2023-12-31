import pandas as pd
from decouple import config
from binance.client import Client

client = Client(config("API_KEY"), config("SECRET_KEY"), testnet= True)

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
    print(klines)

fetch_klines("BTCUSDT")