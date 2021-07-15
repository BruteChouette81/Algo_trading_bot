import  krakenex
from pykrakenapi import KrakenAPI
import plotly.graph_objects as go
import plotly.express as px
import time
import pandas as pd

#calculate the actual average daily trading volume
def adtv(volume, time_laps):
    counter_average = 0
    for vol in volume[-time_laps:]:
        counter_average += float(vol[0])

    return counter_average / time_laps

# verify if the volume is higher than the average volume
def verify_adtv(adtv, live_volume):
    if live_volume > adtv:
        return True
    elif adtv > live_volume:
        return False
    else:
        return False

kraken = krakenex.API()
k = KrakenAPI(kraken)
data = {
        'ma' : [],
        'prices' : []
        }


times = str(int(time.time() - 43200))
ohlc = k.get_ohlc_data('BTCUSD', since=times, ascending=True)

vol = ohlc[0][["volume"]]
print(vol)
#calculate the 30 minute volume average
av = adtv(vol.values.tolist(), 30)
list_vol = vol.values.tolist()
live_vol = float(list_vol[-1:][0][0])
print(live_vol)


btc = ohlc[0][["close"]]

btc.rename(columns={'close':'Price'}, inplace=True)
btc["100ma"] = btc["Price"].rolling(window=100).mean()
btc["13bar"] = btc["Price"].rolling(window=13).mean()
btc["8bar"] = btc["Price"].rolling(window=8).mean()
btc["5bar"] = btc["Price"].rolling(window=5).mean()


fig = go.Figure(data = [go.Candlestick(x = ohlc[0].index,
                                        open = ohlc[0]['open'],
                                        high = ohlc[0]['high'],
                                        low = ohlc[0]['low'],
                                        close = ohlc[0]['close'],
                                        ),
                        go.Scatter(x = ohlc[0].index, y = btc['100ma'], line=dict(color = 'red', width = 1))])

fig.add_trace(go.Scatter(x = ohlc[0].index, y = btc['8bar'], line=dict(color = 'green', width = 1)))

fig.add_trace(go.Scatter(x = ohlc[0].index, y = btc['13bar'], line=dict(color = 'purple', width = 1)))

fig.show()


ma = btc["8bar"].values.tolist()
price = btc["Price"].values.tolist()
data["ma"].append(ma)
data["prices"].append(price)

ma_10min_data = data["ma"][0][-10:] # reversed 
price_10min_data = [price for price in data["prices"][0][-10:]] #reversed(data["prices"][0][-10:])
print(price_10min_data)
print(ma_10min_data)

trend = []
save_price = []
counter = 0
for i in range(0, 10):
    if ma_10min_data[i] < price_10min_data[i]:
        trend.append("uptrend")
        if counter == 0:
            counter = 1

        else:
            counter += 1

    elif ma_10min_data[i] > price_10min_data[i]:
        trend.append("downtrend")
        counter - 1
    
    else:
        trend.append("not_trend")
        continue

print(trend)

volume_trend = verify_adtv(av, live_vol)
print(av)
print(live_vol)
if counter >= 7 and volume_trend:
    print("buy")


elif counter < 7 and volume_trend:
    print("sell")


#trading crypto bot

BALANCE = 10

def get_live_prize():
    pass


class trend_following:
    def __init__(self, data):
        self.data = data

    def algo(self):
        for i in range(self.data):
            if self.data["13bar"].iloc[i] > self.data["Price"].iloc[i]:
                print("buy")

            else:
                print("sell")

    #trend is up and real price is higher than the moving average == up trend = BUY
    #real price is same or lass than the average price == down trend = sell


'''
btc = ohlc[0][["close"]]
list_btc = btc.values.tolist()
print(list_btc)

btc.rename(columns={'close':'Price'}, inplace=True)
btc["100ma"] = btc["Price"].rolling(window=100).mean()
btc["30ma"] = btc["Price"].rolling(window=30).mean()
btc["20ma"] = btc["Price"].rolling(window=20).mean()
btc["5bar"] = btc["Price"].rolling(window=5).mean()



fig = go.Figure(data = [go.Candlestick(x = ohlc[0].index,
                                        open = ohlc[0]['open'],
                                        high = ohlc[0]['high'],
                                        low = ohlc[0]['low'],
                                        close = ohlc[0]['close'],
                                        ),
                        go.Scatter(x = ohlc[0].index, y = btc['5bar'], line=dict(color = 'red', width = 1))])

fig.add_trace(go.Scatter(x = ohlc[0].index, y = btc['100ma'], line=dict(color = 'green', width = 1)))

fig.add_trace(go.Scatter(x = ohlc[0].index, y = btc['20ma'], line=dict(color = 'purple', width = 1)))

fig.show()


ret = kraken.query_public('OHLC', data = {'pair': 'BTCUSD', 'since': times})
mva = ret['result']


for b in mva['XXBTZUSD'][-100:]:
    data['prices'].append(b)

    close = float(b[4])
    data['close'].append(close)

closing = data['close'][-5:]
print(closing)

'''
