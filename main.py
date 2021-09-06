import  krakenex
from pykrakenapi import KrakenAPI
import plotly.graph_objects as go
import plotly.express as px
import time
import json
import argparse
from termcolor import colored
import os
api = krakenex.API()
kraken = KrakenAPI(api)
parser = argparse.ArgumentParser(description='Trading Bot by Thomas Berthiaume')
api.load_key('apikey.txt')

buy = 0
balance = 300
'''
balance = kraken.get_account_balance()
balance = balance["vol"].values.tolist()
balance = float(balance[0]) #- number of money you DONT want to invest.
'''
stock = 'BTCUSD'
krken = False
chart = False



def create_trades(time, buy, sell, stock, price, prc):
    trades = {"time": time,
    "buy": buy,
    "sell": sell,
    "stock": stock,
    "price": price,
    "pourcentage": prc
    }
    return trades

def create_file(trades):
    with open("trades.json", "r+") as file:
        file_data = json.load(file)
        file_data["data"].append(trades)
        file.seek(0)
        json.dump(file_data, file, indent = 4)

def read_file():
    with open("trades.json", "r") as file:
        data = json.load(file)
        prc = 0.0
        for db in data["data"]:
            prc = db["pourcentage"]
        file.close()
    return prc


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

def request_data(stock, kraken):
    times = str(int(time.time() - 43200))
    ohlc = kraken.get_ohlc_data(stock, since=times, ascending=True)
    return ohlc

def calculate_indicator(ohlc, MATIME, ADTVTIME):
    vol = ohlc[0][["volume"]]
    #calculate the 30 minute volume average
    av = adtv(vol.values.tolist(), ADTVTIME)
    list_vol = vol.values.tolist()
    live_vol = float(list_vol[-1:][0][0])
    print(f"live BTCUSD volume: {live_vol}\n")


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
    data = {
        'ma' : [],
        'prices' : []
        }
    ma = btc["ma"].values.tolist()
    price = btc["Price"].values.tolist()
    data["ma"].append(ma)
    data["prices"].append(price)

    ma_10min_data = data["ma"][0][-10:] # reversed 
    price_10min_data = [price for price in data["prices"][0][-10:]] #reversed(data["prices"][0][-10:])
    print(f"10 min. price: {price_10min_data}\n")
    print(f"10 min. moving average: {ma_10min_data}\n")

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
    print("")

    return trend, counter


def verify_transaction(av, live_vol, counter):
    volume_trend = verify_adtv(av, live_vol)
    print(f"average volume: {av}\n")
    if counter >= 7 and volume_trend:
        print(colored('Algorithme detect a: BUY trend', 'green'))
        return True


    elif counter < 7 and volume_trend:
        print(colored('Algorithme detect a: SELL trend', 'red'))
        return False

    else:
        return None

def save_transaction(req):
    pp = req[0][["close"]].values.tolist()
    fprice = [price for price in pp[-1]]
    return float(fprice[0])

def get_prc(price, balance):
    return balance / price


#trading crypto bot
def bot(actived, chart, buy, stop_loss, krken, kraken, balance):
    while actived:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(balance)
        #make the stock request
        req = request_data(stock, kraken)
        #calculate the market inducator
        btc, av, live_vol = calculate_indicator(req, MATIME=matime, ADTVTIME=adtvtime)
        if chart:
            draw(req, btc)
        #run the algorithme
        trend, counter = algo(btc)
        #check if a transaction must be done
        transaction = verify_transaction(av, live_vol, counter)
        stopit = False
        # first if we already have a stock: verify if the price dont pass the stop
        if buy != 0:
            price = save_transaction(req=req)
            stop_balance = balance - (balance * stop_loss)
            btc_prc = read_file()
            live_money = btc_prc * price
            if stop_balance > live_money:
                stopit = True

        # second if we dont have a stock yet and we must buy: create a trnsaction and buy the stock all in ( all cash we put in the bot)
        if transaction == True and buy == 0:
            if krken:
                #change order type
                response = kraken.add_standard_order(pair=stock, type='buy', ordertype='market', price=balance, validate=False)
                print(colored(f'Algorithme buy. resp: {response}', 'green'))

                currenty, prc = kraken.get_trade_volume(fee_info=False)
                #navigate in the dataframe to find prc

            else:
                price = save_transaction(req=req)
                print(price)
                prc = get_prc(float(price), balance)
            
            
            trades = create_trades(time.time(), True, False, stock, balance, float(prc))
            create_file(trades)

            buy = 1
            

        # and finally if we have something and must sell: we calculate the profit and sell all teh prc taht we have ( at preferded profit :) )
        elif transaction == False and buy != 0 or stopit:
            btc_prc = read_file()
            price = save_transaction(req=req)
            live_money = btc_prc * float(price)
            if live_money > balance:
                print("selling at profit")
            else:
                print("selling at loss")
            trades = create_trades(time.time(), False, True, stock, live_money, btc_prc)
            create_file(trades)
            buy = 0
            balance = live_money # or line one balance
            if krken:
                response = kraken.add_standard_order(pair=stock, type='sell', ordertype='market', volume=btc_prc, validate=False)
                print(colored(f'Algorithme sell. resp: {response}', 'red'))


        else:
            print("stand by...\n")

        #repeat each 30 second
        print(f"Number of BTCUSD live: {buy}")
        time.sleep(30)
    

#trend is up and real price is higher than the moving average == up trend = BUY
#real price is same or lass than the average price == down trend = sell

if __name__ == '__main__':
    parser.add_argument('--ma', type=int, help='define mobile average')
    parser.add_argument('--adtv', type=int, help='define adtv')
    parser.add_argument('--chart', type=int, help='draw the bitcoin price')
    parser.add_argument('--stop', type=int, help="put a stop (4 prc is 0.04)")
    parser.add_argument('--kraken', type=int, help="1 for real mode, else put nothing")

    args = parser.parse_args()
    if args.stop:
        stop_loss = args.stop

    else:
        stop_loss = 0.04

    if args.ma:
        matime = args.ma
    else:
        matime = 10

    if args.adtv:
        adtvtime = args.adtv

    else:
        adtvtime = 10

    if args.chart:
        chart = True
    else:
        pass

    if args.kraken:
        krken = True

    else:
        pass

    bot = bot(True, chart, buy, stop_loss, krken, kraken, balance)
    