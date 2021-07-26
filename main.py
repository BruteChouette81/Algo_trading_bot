import  krakenex
from pykrakenapi import KrakenAPI
import plotly.graph_objects as go
import plotly.express as px
import time
import pandas as pd
import json
import argparse
kraken = krakenex.API()
k = KrakenAPI(kraken)
parser = argparse.ArgumentParser(description='Trading Bot by Thomas Berthiaume')

BALANCE = 100
stock = 'BTCUSD'
data = {
        'ma' : [],
        'prices' : []
        }

def create_trades(time, buy, sell, stock, price):
    trades = {"time": time,
    "buy": buy,
    "sell": sell,
    "stock": stock,
    "price": price
    }
    return trades

def create_file(trades):
    json_object = json.dumps(trades)
    with open("trades.json", "w") as file:
        file.write(json_object)

def read_file():
    with open("trades.json", "w") as file:
        data = json.load(file)
    return data["price"]


#calculate the actual average daily trading volume
def adtv(volume, time_laps):
    counter_average = 0
    for vol in volume[-time_laps:]:
        if counter_average == 0:
            counter_average = float(vol[0])

        else:
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

def request_data(stock):
    times = str(int(time.time() - 43200))
    ohlc = k.get_ohlc_data(stock, since=times, ascending=True)
    return ohlc

def calculate_indicator(ohlc, MATIME, ADTVTIME):
    vol = ohlc[0][["volume"]]
    print(vol)
    #calculate the 30 minute volume average
    av = adtv(vol.values.tolist(), ADTVTIME)
    list_vol = vol.values.tolist()
    live_vol = float(list_vol[-1:][0][0])
    print(live_vol)


    btc = ohlc[0][["close"]]

    btc.rename(columns={'close':'Price'}, inplace=True)
    btc["ma"] = btc["Price"].rolling(window=MATIME).mean()

    return btc, av, live_vol

def draw(ohlc, btc):
    fig = go.Figure(data = [go.Candlestick(x = ohlc[0].index,
                                            open = ohlc[0]['open'],
                                            high = ohlc[0]['high'],
                                            low = ohlc[0]['low'],
                                            close = ohlc[0]['close'],
                                            ),
                            go.Scatter(x = ohlc[0].index, y = btc['ma'], line=dict(color = 'red', width = 1))])
    fig.show()


def algo(btc):
    ma = btc["ma"].values.tolist()
    price = btc["Price"].values.tolist()
    data["ma"].append(ma)
    data["prices"].append(price)

    ma_10min_data = data["ma"][0][-10:] # reversed 
    price_10min_data = [price for price in data["prices"][0][-10:]] #reversed(data["prices"][0][-10:])
    print(price_10min_data)
    print(ma_10min_data)

    trend = []
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

    return trend, counter


def verify_transaction(av, live_vol, counter):
    volume_trend = verify_adtv(av, live_vol)
    print(av)
    print(live_vol)
    if counter >= 7 and volume_trend:
        print("buy")
        return True


    elif counter < 7 and volume_trend:
        print("sell")
        return False

    else:
        return None

def save_transaction(req):
    return req[0][["close"]]


#trading crypto bot
def bot(actived):
    while actived:
        req = request_data(stock)
        btc, av, live_vol = calculate_indicator(req, MATIME=matime, ADTVTIME=adtvtime)
        draw(req, btc)
        trend, counter = algo(btc)
        transaction = verify_transaction(av, live_vol, counter)
        print(transaction)
        if transaction == True:
            price = save_transaction(req=req)
            trades = create_trades(time.time(), True, False, stock, price.values.tolist())
            create_file(trades)

        elif transaction == False:
            buy_price = read_file()
            price = save_transaction(req=req)
            if price > buy_price:
                print("selling at profit")
            else:
                print("selling at loss")
            trades = create_trades(time.time(), False, True, stock, price.values.tolist())
            create_file(trades)

        else:
            print("stand by...")

        time.sleep(30)
    

#trend is up and real price is higher than the moving average == up trend = BUY
#real price is same or lass than the average price == down trend = sell

if __name__ == '__main__':
    parser.add_argument('--ma', type=int, help='define mobile average')
    parser.add_argument('--adtv', type=int, help='define adtv')
    args = parser.parse_args()
    if args.ma:
        matime = args.ma
    else:
        matime = 10

    if args.adtv:
        adtvtime = args.adtv

    else:
        adtvtime = 10
    
    bot = bot(True)


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
