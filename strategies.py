import random
import numpy as np
import pandas as pd
import pandas_ta as ta
from tvDatafeed import TvDatafeed, Interval
from utils import *
import requests


class Indicators:
    def __init__(self):
        self.tv = TvDatafeed()

    def get_ohlcv(self, mins, coin):
        if mins == 5:
            data = self.tv.get_hist(symbol=coin, exchange='BINANCE', interval=Interval.in_5_minute, n_bars=288)
        elif mins == 3:
            data = self.tv.get_hist(symbol=coin, exchange='BINANCE', interval=Interval.in_3_minute, n_bars=288)
        elif mins == 15:
            data = self.tv.get_hist(symbol=coin, exchange='BINANCE', interval=Interval.in_15_minute, n_bars=288)
        else:
            data = self.tv.get_hist(symbol=coin, exchange='BINANCE', interval=Interval.in_1_minute, n_bars=288)
        return data

    def get_ma(self, mins, coin):
        ohlc = self.get_ohlcv(mins, coin)
        ma50 = ohlc.ta.ema(50)
        ma100 = ohlc.ta.ema(100)
        ma200 = ohlc.ta.ema(200)

        return {
            'current50': ma50[len(ma50) - 1],
            'current100':ma100[len(ma100) - 1],
            'current200': ma200[len(ma200) - 1],
            'past50': ma50[len(ma50) - 2]
        }

    def rsi_tradingview(self, ohlc: pd.DataFrame, period: int = 14, round_rsi: bool = True):
        delta = ohlc["close"].diff()
        up = delta.copy()
        up[up < 0] = 0
        up = pd.Series.ewm(up, alpha=1 / period).mean()
        down = delta.copy()
        down[down > 0] = 0
        down *= -1
        down = pd.Series.ewm(down, alpha=1 / period).mean()
        rsi = np.where(up == 0, 0, np.where(down == 0, 100, 100 - (100 / (1 + up / down))))

        return np.round(rsi, 2) if round_rsi else rsi

    def stoch_rsi_tradingview(self, ohlc: pd.DataFrame, period=14, smoothK=3, smoothD=3):
        rsi = self.rsi_tradingview(ohlc, period=period, round_rsi=False)
        rsi = pd.Series(rsi)
        stochrsi = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
        stochrsi_K = stochrsi.rolling(smoothK).mean()
        stochrsi_D = stochrsi_K.rolling(smoothD).mean()

        return round(rsi, 2), round(stochrsi_K * 100, 2), round(stochrsi_D * 100, 2)

    def get_stoch_rsi(self, mins, coin):
        ohlc = self.get_ohlcv(mins, coin)
        rsi, stochrsi_K, stochrsi_D = self.stoch_rsi_tradingview(ohlc)
        data = []
        for i, v in rsi.items():
            data.append([stochrsi_K[i], stochrsi_D[i]])

        return data


class Strategies:
    def __init__(self, pr):
        self.pr = pr
        self.ta = Indicators()

        self.call = {
             '1': self.auto_trend,
             '2': self.up_trend,
             '3': self.down_trend,
             '4': self.higher_payout,
             '5': self.lower_payout,
             '6': 'self.manual',
             '7': self.random_strategy,
             '8': self.copy_player,
             '9': self.stochrsi,
             '10': self.candle,
             '11': self.spread,
             '12': self.higher_with_spread_block,
             '13': self.stochrsi_2,
             '14': self.always_bear,
             '15': self.always_bull,
             '16': self.average_true_range,
             '17': self.heikin_ashi,
             '18': self.ichimoku,
        }

    # helpers

    def get_last_alert(self, alert):
        url = f'https://tester-mwb.herokuapp.com/alert/{alert}'
        last_alert = requests.get(url).json()
        last_alert = last_alert['data']

        return last_alert[0]['position']

    def get_payouts(self, epoch):
        if self.pr.dapp == dapps.pancake:
            data = self.pr.pcs_contract.functions.rounds(epoch).call()
            bull_amount = self.pr.w3.fromWei(data[9], 'ether')
            bear_amount = self.pr.w3.fromWei(data[10], 'ether')
            dapp_address = self.pr.PCS_CONTRACT.lower()
            bull_input = '0x5'
            bear_input = '0xa'
        elif self.pr.dapp == dapps.dogebets:
            data = self.pr.dogebets_contract.functions.Rounds(epoch).call()
            bull_amount = self.pr.w3.fromWei(data[1], 'ether')
            bear_amount = self.pr.w3.fromWei(data[2], 'ether')
            dapp_address = self.pr.DOGE_CONTRACT.lower()
            bull_input = '0x9'
            bear_input = '0xd'

        if self.pr.node.startswith('https'):
            pool = self.pr.w3.geth.txpool.content()
            pool = pool.pending
            for txs in pool:
                for tx in pool[txs]:
                    if str(pool[txs][tx]["to"]).lower() == dapp_address:
                        value = self.pr.w3.toInt(hexstr=pool[txs][tx]["value"])
                        value = self.pr.w3.fromWei(value, 'ether')
                        input = pool[txs][tx]["input"]
                        if input.startswith(bull_input):
                            bull_amount += value
                        elif input.startswith(bear_input):
                            bear_amount += value

        bull_multi = (bear_amount / bull_amount) + 1
        bear_multi = (bull_amount / bear_amount) + 1

        return [bull_multi, bear_multi]

    def get_spread(self):
        if self.pr.dapp == dapps.pancake:
            price = self.ta.get_ohlcv(1, 'BNBUSD').tail(1)
            price = float(price['close'][0])
            oracle_price = self.pr.oracle_contract.functions.latestAnswer().call()
            oracle_price = oracle_price / 100000000
            spread_value = (price - oracle_price)
            spread = spread_value * 100 / oracle_price
            return spread
        elif self.pr.dapp == dapps.dogebets:
            price = self.ta.get_ohlcv(1, 'BNBUSDT').tail(1)
            price = float(price['close'][0])
            current_price = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json()
            current_price = round(float(current_price['price']), 1)
            spread_value = (price - current_price)
            spread = spread_value * 100 / current_price
            return spread

    # Non-TA strategies

    def higher_payout(self, mins, coin, epoch):
        payouts = self.get_payouts(epoch)

        if payouts[0] > payouts[1]:
            position = 'bull'
        elif payouts[1] > payouts[0]:
            position = 'bear'
        else:
            position = 'null'

        return position

    def lower_payout(self, mins, coin, epoch):
        payouts = self.get_payouts(epoch)

        if payouts[0] > payouts[1]:
            position = 'bear'
        elif payouts[1] > payouts[0]:
            position = 'bull'
        else:
            position = 'null'

        return position

    def random_strategy(self, *args):
        rand = random.getrandbits(1)
        if rand:
            return 'bull'
        else:
            return 'bear'

    def copy_player(self, epoch, player, timer, factor):
        if self.pr.dapp == dapps.pancake:
            bull_input = '0x5'
            bear_input = '0xa'
        elif self.pr.dapp == dapps.dogebets:
            bull_input = '0x9'
            bear_input = '0xd'

        start_time = time.time()
        count = True
        while True:
            now = time.time()
            if now - start_time <= timer:
                if self.pr.node.startswith('https'):
                    pool = self.pr.w3.geth.txpool.content()
                    pool = pool.pending
                    for txs in pool:
                        for tx in pool[txs]:
                            if str(pool[txs][tx]["from"]).lower() == str(player).lower():
                                input = pool[txs][tx]["input"]
                                if input.startswith(bear_input):
                                    bet_amount = self.pr.w3.toInt(hexstr=pool[txs][tx]["value"]) // float(factor)
                                    return ['bear', bet_amount]
                                if input.startswith(bull_input):
                                    bet_amount = self.pr.w3.toInt(hexstr=pool[txs][tx]["value"]) // float(factor)
                                    return ['bull', bet_amount]
                else:
                    count = True
                if count:
                    if self.pr.dapp == dapps.pancake:
                        ledger = self.pr.pcs_contract.functions.ledger(epoch, player).call()
                    elif self.pr.dapp == dapps.dogebets:
                        ledger = self.pr.dogebets_contract.functions.Bets(epoch, player).call()
                    if ledger[1] > 0:
                        bet_amount = ledger[1] // int(factor)
                        if ledger[0] == 0:
                            return ['bull', bet_amount]
                        elif ledger[0] == 1:
                            return ['bear', bet_amount]
                    else:
                        count = False


            else:
                return ['', 0]

    def always_bear(self, *args):
        return 'bear'

    def always_bull(self, *args):
        return 'bull'

    # TA strategies:

    def higher_with_spread_block(self, mins, coin, epoch):
        payouts = self.get_payouts(epoch)
        spread = self.get_spread()

        if payouts[0] > payouts[1] and spread < 0.13:
            position = 'bull'
        elif payouts[1] > payouts[0] and spread > -0.13:
            position = 'bear'
        else:
            position = 'null'

        return position

    def spread(self, *args):
        spread = self.get_spread()
        if spread >= 0.13:
            position = 'bull'
        elif spread <= -0.13:
            position = 'bear'
        else:
            position = 'null'

        return position

    def auto_trend(self, mins, coin, *args):
        if self.pr.dapp == dapps.pancake:
            ma = self.ta.get_ma(mins, coin)
            stoch_rsi = self.ta.get_stoch_rsi(mins, coin)
        elif self.pr.dapp == dapps.dogebets:
            ma = self.ta.get_ma(mins, 'BNBUSDT')
            stoch_rsi = self.ta.get_stoch_rsi(mins, 'BNBUSDT')
        data = stoch_rsi[-2:]

        if ma['current50'] > ma['past50'] and ma['current100'] > ma['current200'] and data[1][0] >= data[0][0]:
            position = 'bull'
        elif ma['current50'] < ma['past50'] and ma['current100'] < ma['current200'] and data[1][0] <= data[0][0]:
            position = 'bear'
        else:
            position = 'null'

        return position

    def up_trend(self, mins, coin, *args):
        if self.pr.dapp == dapps.pancake:
            ma = self.ta.get_ma(mins, coin)
            stoch_rsi = self.ta.get_stoch_rsi(mins, coin)
        elif self.pr.dapp == dapps.dogebets:
            ma = self.ta.get_ma(mins, 'BNBUSDT')
            stoch_rsi = self.ta.get_stoch_rsi(mins, 'BNBUSDT')
        data = stoch_rsi[-2:]
        if ma['current50'] > ma['past50'] and ma['current100'] > ma['current200'] and data[1][0] >= data[0][0]:
            position = 'bull'
        else:
            position = 'null'

        return position

    def down_trend(self, mins, coin, *args):
        if self.pr.dapp == dapps.pancake:
            ma = self.ta.get_ma(mins, coin)
            stoch_rsi = self.ta.get_stoch_rsi(mins, coin)
        elif self.pr.dapp == dapps.dogebets:
            ma = self.ta.get_ma(mins, 'BNBUSDT')
            stoch_rsi = self.ta.get_stoch_rsi(mins, 'BNBUSDT')

        data = stoch_rsi[-2:]

        if ma['current50'] < ma['past50'] and ma['current100'] < ma['current200'] and data[1][0] <= data[0][0]:
            position = 'bear'
        else:
            position = 'null'

        return position

    def candle(self, mins, coin, *args):
        if self.pr.dapp == dapps.pancake:
            ohlc = self.ta.get_ohlcv(mins, coin).tail(1)
        elif self.pr.dapp == dapps.dogebets:
            ohlc = self.ta.get_ohlcv(mins, 'BNBUSDT').tail(1)
        close = float(ohlc['close'][0])
        high = float(ohlc['high'][0])
        low = float(ohlc['low'][0])

        down_wyck = ((high - close) * 100) / close
        up_wyck = ((low - close) * 100) / close
        up_wyck = abs(up_wyck)

        if down_wyck > up_wyck and down_wyck > 0.13:
            position = 'bear'
        elif up_wyck > down_wyck and up_wyck > 0.13:
            position = 'bull'
        else:
            position = 'null'

        return position

    def stochrsi(self, mins, coin, *args):
        if self.pr.dapp == dapps.pancake:
            stoch_rsi = self.ta.get_stoch_rsi(mins, coin)
        elif self.pr.dapp == dapps.dogebets:
            stoch_rsi = self.ta.get_stoch_rsi(mins, 'BNBUSDT')
        data = stoch_rsi[-2:]
        if 20 > data[1][0] > data[0][0]:
            position = 'bull'
        elif 80 < data[1][0] < data[0][1]:
            position = 'bear'
        elif data[1][0] > 20 and data[0][1] < 20:
            position = 'bull'
        elif data[1][0] < 80 and data[0][1] > 80:
            position = 'bear'
        else:
            position = 'null'

        return position

    def stochrsi_2(self, mins, coin, epoch):
        if self.pr.dapp == dapps.pancake:
            stoch_rsi = self.ta.get_stoch_rsi(mins, coin)
        elif self.pr.dapp == dapps.dogebets:
            stoch_rsi = self.ta.get_stoch_rsi(mins, 'BNBUSDT')
        data = stoch_rsi[-2:]
        if 20 > data[1][0] > data[0][0]:
            position = 'bull'
        elif 80 < data[1][0] < data[0][1]:
            position = 'bear'
        elif data[1][0] > 20 and data[0][1] < 20:
            position = 'bull'
        elif data[1][0] < 80 and data[0][1] > 80:
            position = 'bear'
        else:
            position = 'null'

        higher_payout_position = self.higher_payout(mins, coin, epoch)
        if position != higher_payout_position:
            position = 'null'

        return position

    def average_true_range(self, *args):
        position = self.get_last_alert('AverageTrueRange')
        return position

    def heikin_ashi(self, *args):
        position = self.get_last_alert('HeikinAshi')
        return position

    def ichimoku(self, *args):
        position = self.get_last_alert('Ichimoku')
        return position