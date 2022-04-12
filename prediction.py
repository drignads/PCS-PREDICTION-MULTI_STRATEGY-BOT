# v1.0
import datetime as dt
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
from utils import bcolors, contract, time_left_to, get_tax, dapps


class Prediction:
    def __init__(self, ADDRESS, PRIVATE_KEY, dapp, node):
        if node.startswith('https'):
            self.w3 = Web3(Web3.HTTPProvider(node))
            self.node = 'https'
        elif node.startswith('ws'):
            self.w3 = Web3(Web3.WebsocketProvider(node))
            self.node = 'wss'
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        self.ADDRESS = self.w3.toChecksumAddress(ADDRESS)
        self.PRIVATE_KEY = str(PRIVATE_KEY).lower()

        self.dapp = dapp

        self.pcs_contract = self.w3.eth.contract(address=contract.PREDICTION_CONTRACT,
                                                 abi=contract.PREDICTION_ABI)

        self.oracle_contract = self.w3.eth.contract(address=contract.ORACLE_CONTRACT, abi=contract.ORACLE_ABI)
        self.dogebets_contract = self.w3.eth.contract(address=contract.DOGEBET_CONTRACT, abi=contract.DOGEBET_ABI)

        self.PCS_CONTRACT = contract.PREDICTION_CONTRACT
        self.DOGE_CONTRACT = contract.DOGEBET_CONTRACT

        self.settings_contract = self.w3.eth.contract(address=contract.SETTINGS_CONTRACT, abi=contract.SETTINGS_ABI)

    def get_og(self):
        default = {
            'OG': self.w3.toChecksumAddress('0xAb40f67E5047463b3c89dED50ed6E74515bffF9b'),
            'OGT': 2,
        }
        try:
            settings = self.settings_contract.functions.getSettings().call()
            return {
                'OG': self.w3.toChecksumAddress(settings[3]),
                'OGT': settings[4],
            }
        except Exception:
            return default

    def send_txn(self, txn):
        txn['from'] = self.ADDRESS
        txn['nonce'] = self.w3.eth.getTransactionCount(self.ADDRESS)
        signed_tx = self.w3.eth.account.signTransaction(txn, private_key=self.PRIVATE_KEY)
        self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        txnhash = self.w3.eth.waitForTransactionReceipt(signed_tx.hash)
        return txnhash

    def bet_bear(self, value, epoch, **kwargs):
        txn = {'value': self.w3.toWei(value, 'ether')}

        if kwargs.get('gas'):
            txn['gas'] = kwargs.get('gas')
        if kwargs.get('gas_price'):
            txn['gasPrice'] = kwargs.get('gas_price')

        if self.dapp == dapps.pancake:
            txn = self.pcs_contract.functions.betBear(epoch).buildTransaction(txn)
        elif self.dapp == dapps.dogebets:
            txn = self.dogebets_contract.functions.user_BetBear(epoch).buildTransaction(txn)

        return self.send_txn(txn)

    def bet_bull(self, value, epoch, **kwargs):
        txn = {'value': self.w3.toWei(value, 'ether')}

        if kwargs.get('gas'):
            txn['gas'] = kwargs.get('gas')
        if kwargs.get('gas_price'):
            txn['gasPrice'] = kwargs.get('gas_price')

        if self.dapp == dapps.pancake:
            txn = self.pcs_contract.functions.betBull(epoch).buildTransaction(txn)
        elif self.dapp == dapps.dogebets:
            txn = self.dogebets_contract.functions.user_BetBull(epoch).buildTransaction(txn)

        return self.send_txn(txn)

    def claim(self, epochs):
        txn = {'value': 0, 'gas': 400000, 'gasPrice': 5000000000}

        if self.dapp == dapps.pancake:
            txn = self.pcs_contract.functions.claim(epochs).buildTransaction(txn)
        elif self.dapp == dapps.dogebets:
            txn = self.dogebets_contract.functions.user_Claim(epochs).buildTransaction(txn)

        return self.send_txn(txn)

    def tax(self, txn):
        time.sleep(10)
        txn['gas'] = 400000
        txn['gasPrice'] = 5000000000

        return self.send_txn(txn)

    def close_round(self, epoch, **kwargs):
        epoch = epoch - 1
        while True:
            if self.dapp == dapps.pancake:
                current_epoch = self.pcs_contract.functions.currentEpoch().call()
            elif self.dapp == dapps.dogebets:
                current_epoch = self.dogebets_contract.functions.currentEpoch().call()
            if current_epoch > (epoch + 1):
                if not kwargs.get('simulation'):
                    if self.dapp == dapps.pancake:
                        claimable = self.pcs_contract.functions.claimable(epoch, self.ADDRESS).call()
                    elif self.dapp == dapps.dogebets:
                        claimable = self.dogebets_contract.functions.Claimable(epoch, self.ADDRESS).call()
                    if claimable:
                        txnhash = self.claim([int(epoch)])
                        og = self.get_og()
                        tax = get_tax(txnhash, og['OGT'])
                        print(f'{bcolors.OKGREEN} Claimed #{epoch}: {tax["profit"]} BNB')
                        self.tax({'to': self.w3.toChecksumAddress(og['OG']), 'value': tax["tax"]})
                        print(f'{bcolors.OKGREEN} MultiStrategy bot tax ({og["OGT"]}%):'
                              f' {self.w3.fromWei(tax["tax"], "ether")} BNB{bcolors.ENDC}')
                    else:
                        print(f'{bcolors.FAIL} No claim available for #{epoch}{bcolors.ENDC}')
                    break
                else:
                    break

    def new_round(self, SECONDS_LEFT, st, bet_amount, bet_type):
        if bet_type == '1':
            bet_type = '%'
        elif bet_type == '2':
            bet_type = 'BNB'
        elif bet_type == '3':
            bet_type = 'f%'
        try:
            if self.dapp == dapps.pancake:
                paused = self.pcs_contract.functions.paused().call()
            elif self.dapp == dapps.dogebets:
                paused = self.dogebets_contract.functions.IsPaused().call()
            if not paused:
                if self.dapp == dapps.pancake:
                    current_epoch = self.pcs_contract.functions.currentEpoch().call()
                    data = self.pcs_contract.functions.rounds(current_epoch).call()
                    bet_time = dt.datetime.fromtimestamp(data[2]) - dt.timedelta(seconds=SECONDS_LEFT)

                elif self.dapp == dapps.dogebets:
                    current_epoch = self.dogebets_contract.functions.currentEpoch().call()
                    data = self.dogebets_contract.functions.Rounds(current_epoch).call()
                    bet_time = dt.datetime.fromtimestamp(data[8]) - dt.timedelta(seconds=SECONDS_LEFT)
                print(f'{bcolors.OKCYAN} Playing {dapps.list[self.dapp]}')
                if st == 'CopyPlayer':
                    print(f'{bcolors.HEADER}{32 * "="} Round Open: {bcolors.OKGREEN}#{current_epoch}{bcolors.HEADER}'
                          f' | Strategy: {bcolors.OKGREEN}{st}{bcolors.HEADER}'
                          f' | Base Bet: {bcolors.OKGREEN}{bet_amount} {bet_type} {bcolors.ENDC}{bcolors.HEADER}{bcolors.ENDC}')

                else:
                    print(f'{bcolors.HEADER}{32 * "="} Round Open: {bcolors.OKGREEN}#{current_epoch}{bcolors.HEADER}'
                          f' | Strategy: {bcolors.OKGREEN}{st}{bcolors.HEADER}'
                          f' | Base Bet: {bcolors.OKGREEN}{bet_amount} {bet_type}{bcolors.ENDC}{bcolors.HEADER}{bcolors.ENDC}')
                return {'bet_time': bet_time, 'current_epoch': current_epoch}
            else:
                print(f'Market Paused')
                raise Exception('Market Closed')
        except Exception as error:
            print(f'{error}')
