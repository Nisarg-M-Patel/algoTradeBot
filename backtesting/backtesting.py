import numpy as np
import pandas as pd
from datetime import datetime
import vectorbt as vbt

btc_price = pd.read_csv("data.csv")[['timestamp','close']]
btc_price['date'] = pd.to_datetime( btc_price['timestamp'], unit= 's')
btc_price = btc_price.set_index('date')['close']

rsi = vbt.RSI.run(btc_price, window = 14, short_name = 'rsi')

entries = rsi.rsi_crossed_below(30)
exits = rsi.rsi_crossed_above(70)

pf = vbt.Portfolio.from_signals(btc_price, entries, exits)


print(pf.stats())


