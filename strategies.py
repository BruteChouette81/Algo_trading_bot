from termcolor import colored

class get_analisys:
    def __init__(self, ohlc, matime, adtvtime):
        self.matime = matime
        self.ohlc = ohlc
        self.adtvtime = adtvtime

    #calculate the actual average daily trading volume
    def adtv(self, volume, time_laps):
        counter_average = 0
        for vol in volume[-time_laps:]:
            if counter_average == 0:
                counter_average = float(vol[0])

            else:
                counter_average += float(vol[0])
        return counter_average / time_laps

    def calculate_indicator(self):
        vol = self.ohlc[0][["volume"]]
        #calculate the 30 minute volume average
        av = self.adtv(vol.values.tolist(), self.adtvtime)
        list_vol = vol.values.tolist()
        live_vol = float(list_vol[-1:][0][0])
        print(f"live BTCUSD volume: {live_vol}\n")


        btc = self.ohlc[0][["close"]]

        btc.rename(columns={'close':'Price'}, inplace=True)
        btc["ma"] = btc["Price"].rolling(window=self.matime).mean()

        return btc, av, live_vol
    
    



class strategie_base:
    def __init__(self, ohlc, matime, adtvtime):
        self.btc, self.av, self.live_vol, = get_analisys(ohlc, matime, adtvtime).calculate_indicator()
    

    # verify if the volume is higher than the average volume
    def verify_adtv(self,adtv, live_volume):
        if live_volume > adtv:
            return True
        elif adtv > live_volume:
            return False
        else:
            return False

    def algo(self):
        data = {
            'ma' : [],
            'prices' : []
            }
        ma = self.btc["ma"].values.tolist()
        price = self.btc["Price"].values.tolist()
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

        volume_trend = self.verify_adtv(self.av, self.live_vol)
        print(f"average volume: {self.av}\n")
        if counter >= 7 and volume_trend:
            print(colored('Algorithme detect a: BUY trend', 'green'))
            return True


        elif counter < 7 and volume_trend:
            print(colored('Algorithme detect a: SELL trend', 'red'))
            return False

        else:
            return None
