import random
import time
import datetime as dt
from web3 import Web3
from web3.middleware import geth_poa_middleware
from contract import PREDICTION_ABI, PREDICTION_CONTRACT


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

# IF TRUE, WHEN BNB BALANCE IS BELLOW BNB_LIMIT
# CLAIM ROUNDS INSIDE RANGE (CURRENT ROUND - RANGE)
RANGE = 100
BNB_LIMIT = 0.1
CLAIM = True

# V2 CONTRACT
predictionContract = w3.eth.contract(address=PREDICTION_CONTRACT, abi=PREDICTION_ABI)


def bet_bull(value, epoch):
    txn = predictionContract.functions.betBull(epoch).buildTransaction({
        'from': ADDRESS,
        'nonce': w3.eth.getTransactionCount(ADDRESS),
        'value': value,
        'gas': GAS,
        'gasPrice': GAS_PRICE,
    })
    signed_txn = w3.eth.account.signTransaction(txn, private_key=PRIVATE_KEY)
    w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f'{w3.eth.waitForTransactionReceipt(signed_txn.hash)}')


def bet_bear(value, epoch):
    txn = predictionContract.functions.betBear(epoch).buildTransaction({
        'from': ADDRESS,
        'nonce': w3.eth.getTransactionCount(ADDRESS),
        'value': value,
        'gas': GAS,
        'gasPrice': GAS_PRICE,
    })
    signed_txn = w3.eth.account.signTransaction(txn, private_key=PRIVATE_KEY)
    w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f'{w3.eth.waitForTransactionReceipt(signed_txn.hash)}')
    
    
def claim(epochs):
    txn = predictionContract.functions.claim(epochs).buildTransaction({
        'from': ADDRESS,
        'nonce': w3.eth.getTransactionCount(ADDRESS),
        'value': 0,
        'gas': 800000,
        'gasPrice': 5000000000,
    })
    signed_txn = w3.eth.account.signTransaction(txn, private_key=PRIVATE_KEY)
    w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f'{w3.eth.waitForTransactionReceipt(signed_txn.hash)}')

    
def fetchClaimable():
    epochs = []
    current = predictionContract.functions.currentEpoch().call()
    epoch = current - 2
    stop = epoch - RANGE

    while epoch >= stop:
        claimable = predictionContract.functions.claimable(epoch, ADDRESS).call()
        if claimable:
            epochs.append(epoch)
        epoch -= 1
    return epochs


def handleClaim():
    myBalance = w3.eth.getBalance(ADDRESS)
    myBalance = w3.fromWei(myBalance, 'ether')
    print(f'My Balance:  {myBalance:.5f} | Limit {BNB_LIMIT}')
    if myBalance <= BNB_LIMIT:
        print(f'Balance Bellow {BNB_LIMIT}, fetching claimable rounds...%')
        epochs = fetchClaimable()
        if len(epochs) > 0:
            print(f'Attempting to claim {len(epochs)} rounds...%\n {epochs}')
            claim(epochs)
        else:
            print(f'Sorry, no rounds to claim')
    

def makeBet(epoch):
    """
    Add your bet logic here

    This example bet random either up or down:
    """
    value = w3.toWei(0.01, 'ether')
    rand = random.getrandbits(1)
    if rand:
        print(f'Going Bull #{epoch} | {value} BNB  ')
        bet_bull(value, epoch)
    else:
        print(f'Going Bear #{epoch} | {value} BNB  ')
        bet_bear(value, epoch)
        

def newRound():
    try:
        current_epoch = predictionContract.functions.currentEpoch().call()
        data = predictionContract.functions.rounds(current_epoch).call()
        bet_time = dt.datetime.fromtimestamp(data[2]) - dt.timedelta(seconds=SECONDS_LEFT)
        if CLAIM:
            handleClaim()
        print(f'New round: #{current_epoch}')
        return [bet_time, current_epoch]
    except Exception as error:
        print(f'New round fail - {error}')


def run():
    current_round = newRound()
    while True:
        try:
            now = dt.datetime.now()
            if now >= current_round[0]:
                makeBet(current_round[1])
                time.sleep(40)
                current_round = newRound()
        except Exception as error:
            print(f'Restarting...% {error}')
            current_round = newRound()


if __name__ == '__main__':
    run()

