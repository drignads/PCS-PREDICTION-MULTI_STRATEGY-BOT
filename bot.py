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
    print(f'{w3.eth.waitForTransactionReceipt(signed_tx.hash)}')


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
    print(f'{w3.eth.waitForTransactionReceipt(signed_tx.hash)}')
    
    
def claim(epochs):
    claim = predictionContract.functions.claim(epochs).buildTransaction({
        'from': ADDRESS,
        'nonce': w3.eth.getTransactionCount(ADDRESS),
        'value': 0,
        'gas': 800000,
        'gasPrice': 5000000000,
    })
    signed_tx = w3.eth.account.signTransaction(claim, private_key=PRIVATE_KEY)
    w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(f'{w3.eth.waitForTransactionReceipt(signed_tx.hash)}') 

    
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
        epochs = fetchClaimable()
        print(f'Balance Bellow {BNB_LIMIT} | Attempting to claim {len(epochs)} rounds...%\n {epochs}')
        claim(epochs)
    

def makeBet(epoch):
    """
    Add your bet logic here

    This example bet random either up or down:
    """
    value = w3.toWei(0.01, 'ether')
    rand = random.getrandbits(1)
    if rand:
        print(f'Going Bull #{epoch} | {value} BNB  ')
        betBull(value, epoch)        
    else:
        print(f'Going Bear #{epoch} | {value} BNB  ')
        betBear(value, epoch)
        


def newRound():
    try:
        current = predictionContract.functions.currentEpoch().call()
        data = predictionContract.functions.rounds(current).call()
        bet_time = dt.datetime.fromtimestamp(data[2]) - dt.timedelta(seconds=SECONDS_LEFT)
        if AUTO_CLAIM:
            handleClaim()
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
                time.sleep(130)
                round = newRound()
        except Exception as e:
            print(f'(error) Restarting...% {e}')
            round = newRound()


if __name__ == '__main__':
    run()

