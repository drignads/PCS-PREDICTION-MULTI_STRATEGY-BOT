import random
import numpy as np
import pandas_ta as ta
from tvDatafeed import TvDatafeed, Interval
from inputimeout import inputimeout, TimeoutOccurred
from utils import *


class Indicators:
    def __init__(self):
        self.tv = TvDatafeed()

    def get_bnb_ohlcv_5min(self):
        data = self.tv.get_hist(symbol='BNBUSD', exchange='BINANCE', interval=Interval.in_5_minute, n_bars=288)
        return data

    def getMA(self):
        ohlc = self.get_bnb_ohlcv_5min()
        ma = ohlc.ta.ema(50)
        currentma = ma[len(ma) - 1]
        pastma = ma[len(ma) - 2]

        return [currentma, pastma]


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
            '6': 'Manual',
            '7': self.random_strategy,
            '8': self.copy_player,
        }

    def get_payouts(self, epoch):
        data = self.pr.prediction_contract.functions.rounds(epoch).call()
        bull_amount = self.pr.w3.fromWei(data[9], 'ether')
        bear_amount = self.pr.w3.fromWei(data[10], 'ether')

        pool = self.pr.w3.geth.txpool.content()
        pool = pool.pending
        for txs in pool:
            for tx in pool[txs]:
                if str(pool[txs][tx]["to"]).lower() == self.pr.CONTRACT.lower():
                    value = self.pr.w3.toInt(hexstr=pool[txs][tx]["value"])
                    value = self.pr.w3.fromWei(value, 'ether')
                    input = pool[txs][tx]["input"]
                    if input.startswith('0x5'):
                        bull_amount += value
                    elif input.startswith('0xa'):
                        bear_amount += value

        bull_multi = (bear_amount / bull_amount) + 1
        bear_multi = (bull_amount / bear_amount) + 1

        return [bull_multi, bear_multi]

    def random_strategy(self, epoch):
        rand = random.getrandbits(1)
        if rand:
            return 'bull'
        else:
            return 'bear'

    def copy_player(self, epoch, player, timer, factor):
        bull = '0x57fb096f'
        bear = '0xaa6b873a'
        start_time = time.time()
        count = True
        while True:
            now = time.time()
            if now - start_time <= timer:
                pool = self.pr.w3.geth.txpool.content()
                pool = pool.pending
                for txs in pool:
                    for tx in pool[txs]:
                        if str(pool[txs][tx]["from"]).lower() == str(player).lower():
                            input = pool[txs][tx]["input"]
                            if input == bear:
                                bet_amount = self.pr.w3.toInt(hexstr=pool[txs][tx]["value"]) // int(factor)
                                return ['bear', bet_amount]
                            if input == bull:
                                bet_amount = self.pr.w3.toInt(hexstr=pool[txs][tx]["value"]) // int(factor)
                                return ['bull', bet_amount]
                if count:
                    ledger = self.pr.prediction_contract.functions.ledger(epoch, player).call()
                    if ledger[1] > 0:
                        bet_amount = ledger[1] // int(factor)
                        if ledger[0] == 0:
                            return ['bull', bet_amount]
                        elif ledger[0] == 1:
                            return ['bear', bet_amount]
                    else:
                        count = False
                time.sleep(0.1)

            else:
                return ['', 0]

    def auto_trend(self, *args):
        ma = self.ta.getMA()
        currentma = ma[0]
        pastma = ma[1]

        if currentma > pastma:
            position = 'bull'
        elif currentma < pastma:
            position = 'bear'
        else:
            position = ''

        return position

    def up_trend(self, *args):
        ma = self.ta.getMA()
        currentma = ma[0]
        pastma = ma[1]

        if currentma > pastma:
            position = 'bull'
        else:
            position = ''

        return position

    def down_trend(self, *args):
        ma = self.ta.getMA()
        currentma = ma[0]
        pastma = ma[1]

        if currentma < pastma:
            position = 'bear'
        else:
            position = ''

        return position

    def higher_payout(self, epoch):
        payouts = self.get_payouts(epoch)

        if payouts[0] > payouts[1]:
            position = 'bull'
        elif payouts[1] > payouts[0]:
            position = 'bear'
        else:
            position = ''
        return position

    def lower_payout(self, epoch):
        payouts = self.get_payouts(epoch)

        if payouts[0] > payouts[1]:
            position = 'bear'
        elif payouts[1] > payouts[0]:
            position = 'bull'
        else:
            position = ''
        return position