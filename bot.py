import random
import time
import datetime as dt
from web3 import Web3
from web3.middleware import geth_poa_middleware
from config import PREDICTION_ABI, PREDICTION_CONTRACT

# BSC NODE
w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org/'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# YOU
ADDRESS = w3.toChecksumAddress('ADDRESS')
PRIVATE_KEY = str('PRIVATE_KEY').lower()

# TX SETTING
GAS = 400000
GAS_PRICE = 5000000000

# SECONDS LEFT BET AT
SECONDS_LEFT = 8

# V2 CONTRACT
predictionContract = w3.eth.contract(address=PREDICTION_CONTRACT, abi=PREDICTION_ABI)


def betBull(value, round):
    bull_bet = predictionContract.functions.betBull(round).buildTransaction({
        'from': ADDRESS,
        'nonce': w3.eth.getTransactionCount(ADDRESS),
        'value': value,
        'gas': GAS,
        'gasPrice': GAS_PRICE,
    })
    signed_tx = w3.eth.account.signTransaction(bull_bet, private_key=PRIVATE_KEY)
    w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(f'{bull_bet}')


def betBear(value, round):
    bear_bet = predictionContract.functions.betBear(round).buildTransaction({
        'from': ADDRESS,
        'nonce': w3.eth.getTransactionCount(ADDRESS),
        'value': value,
        'gas': GAS,
        'gasPrice': GAS_PRICE,
    })
    signed_tx = w3.eth.account.signTransaction(bear_bet, private_key=PRIVATE_KEY)
    w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(f'{bear_bet}')


def makeBet(epoch):
    """
    Add your bet logic here

    This example bet random either up or down:
    """
    value = w3.toWei(0.01, 'ether')
    rand = random.getrandbits(1)
    if rand:
        betBull(value, epoch)
        print(f'Going Bull #{epoch} | {value} BNB  ')
    else:
        betBear(value, epoch)
        print(f'Going Bear #{epoch} | {value} BNB  ')


def newRound():
    try:
        current = predictionContract.functions.currentEpoch().call()
        data = predictionContract.functions.rounds(current).call()
        bet_time = dt.datetime.fromtimestamp(data[2]) - dt.timedelta(seconds=SECONDS_LEFT)
        print(f'New round: #{current}')
        return [bet_time, current]
    except Exception as e:
        print(f'New round fail - {e}')


def run():
    round = newRound()
    n = True
    while n:
        try:
            now = dt.datetime.now()
            if now >= round[0]:
                makeBet(round[1])
                time.sleep(180)
                round = newRound()
        except Exception as e:
            print(f'(error) Restarting...% {e}')
            round = newRound()


if __name__ == '__main__':
    run()

