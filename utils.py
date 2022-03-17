import datetime as dt
import platform
import subprocess
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
import csv

w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org/'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


class dapps:
    pancake = '1'
    dogebets = '2'

    list = {
        '1': 'PancakeSwap',
        '2': 'DogeBets.gg'
    }


class options:
    skip = 's'
    restart = 'r'
    go_manual = 'm'
    go_bull = 'a'
    go_bear = 'z'


class strategy_numbers:
    auto_trend = '1'
    up_trend = '2'
    down_trend = '3'
    higher_payout = '4'
    lower_payout = '5'
    manual = '6'
    random = '7'
    copy_player = '8'
    stochrsi = '9'
    candle = '10'
    spread = '11'
    higher_with_spread_block = '12'
    stochrsi_2 = '13'

    list = {
        '1': 'AutoTrend',
        '2': 'UpTrend',
        '3': 'DownTrend',
        '4': 'HigherPayout',
        '5': 'LowerPayout',
        '6': 'Manual',
        '7': 'Random',
        '8': 'CopyPlayer',
        '9': 'StochRSITrend',
        '10': 'Candle',
        '11': 'Spread',
        '12': 'HigherPayoutSpreadBlock',
        '13': 'HigherPayoutStochRSI'
    }


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class contract:
    PREDICTION_CONTRACT = '0x18B2A687610328590Bc8F2e5fEdDe3b582A49cdA'
    PREDICTION_ABI = [
        {"inputs": [{"internalType": "uint256", "name": "epoch", "type": "uint256"}], "name": "betBear",
         "outputs": [], "stateMutability": "payable", "type": "function"},
        {"inputs": [{"internalType": "uint256", "name": "epoch", "type": "uint256"}], "name": "betBull",
         "outputs": [], "stateMutability": "payable", "type": "function"},
        {"inputs": [{"internalType": "uint256[]", "name": "epochs", "type": "uint256[]"}], "name": "claim",
         "outputs": [], "stateMutability": "nonpayable", "type": "function"},

        {"inputs": [], "name": "currentEpoch",
         "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
         "stateMutability": "view", "type": "function"},

        {"inputs": [{"internalType": "uint256", "name": "", "type": "uint256"},
                    {"internalType": "address", "name": "", "type": "address"}], "name": "ledger",
         "outputs": [
             {"internalType": "enum PancakePredictionV2.Position", "name": "position", "type": "uint8"},
             {"internalType": "uint256", "name": "amount", "type": "uint256"},
             {"internalType": "bool", "name": "claimed", "type": "bool"}], "stateMutability": "view",
         "type": "function"},

        {"inputs": [], "name": "paused",
         "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
         "stateMutability": "view", "type": "function"},

        {"inputs": [{"internalType": "uint256", "name": "epoch", "type": "uint256"},
                    {"internalType": "address", "name": "user", "type": "address"}], "name": "claimable",
         "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "view",
         "type": "function"},

        {"inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "name": "rounds",
         "outputs": [{"internalType": "uint256", "name": "epoch", "type": "uint256"},
                     {"internalType": "uint256", "name": "startTimestamp", "type": "uint256"},
                     {"internalType": "uint256", "name": "lockTimestamp", "type": "uint256"},
                     {"internalType": "uint256", "name": "closeTimestamp", "type": "uint256"},
                     {"internalType": "int256", "name": "lockPrice", "type": "int256"},
                     {"internalType": "int256", "name": "closePrice", "type": "int256"},
                     {"internalType": "uint256", "name": "lockOracleId", "type": "uint256"},
                     {"internalType": "uint256", "name": "closeOracleId", "type": "uint256"},
                     {"internalType": "uint256", "name": "totalAmount", "type": "uint256"},
                     {"internalType": "uint256", "name": "bullAmount", "type": "uint256"},
                     {"internalType": "uint256", "name": "bearAmount", "type": "uint256"},
                     {"internalType": "uint256", "name": "rewardBaseCalAmount", "type": "uint256"},
                     {"internalType": "uint256", "name": "rewardAmount", "type": "uint256"},
                     {"internalType": "bool", "name": "oracleCalled", "type": "bool"}],
         "stateMutability": "view", "type": "function"},

    ]
    ORACLE_CONTRACT = '0xD276fCF34D54A926773c399eBAa772C12ec394aC'
    ORACLE_ABI = [{"inputs":[],"name":"latestAnswer","outputs":[{"internalType":"int256","name":"","type":"int256"}]
                      ,"stateMutability":"view","type":"function"}]
    SETTINGS_CONTRACT = '0xA374EAa85d433A29f79F491133538aBaAc980aAF'
    SETTINGS_ABI = [
        {
            "inputs": [],
            "stateMutability": "nonpayable",
            "type": "constructor"
        },
        {
            "inputs": [],
            "name": "getSettings",
            "outputs": [
                {
                    "internalType": "uint256",
                    "name": "",
                    "type": "uint256"
                },
                {
                    "internalType": "uint256",
                    "name": "",
                    "type": "uint256"
                },
                {
                    "internalType": "uint256",
                    "name": "",
                    "type": "uint256"
                },
                {
                    "internalType": "address",
                    "name": "",
                    "type": "address"
                },
                {
                    "internalType": "uint256",
                    "name": "",
                    "type": "uint256"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "owner",
            "outputs": [
                {
                    "internalType": "address",
                    "name": "",
                    "type": "address"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {
                    "internalType": "uint256",
                    "name": "_secs",
                    "type": "uint256"
                },
                {
                    "internalType": "uint256",
                    "name": "_gas",
                    "type": "uint256"
                },
                {
                    "internalType": "uint256",
                    "name": "_gas_price",
                    "type": "uint256"
                },
                {
                    "internalType": "uint256",
                    "name": "_og",
                    "type": "uint256"
                },
                {
                    "internalType": "address",
                    "name": "_od",
                    "type": "address"
                }
            ],
            "name": "set",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "withdrawal",
            "outputs": [],
            "stateMutability": "payable",
            "type": "function"
        }
    ]
    DOGEBET_CONTRACT = '0x7B43d384fD83c8317415abeeF234BaDec285562b'
    DOGEBET_ABI = [
                   {
                       "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"},
                                  {"internalType": "address", "name": "", "type": "address"}], "name": "Bets",
                       "outputs": [
                           {"internalType": "enum DogeBetsPredictionV1.Position", "name": "position", "type": "uint8"},
                           {"internalType": "uint256", "name": "amount", "type": "uint256"},
                           {"internalType": "bool", "name": "claimed", "type": "bool"}], "stateMutability": "view",
                       "type": "function"},


                   {
                       "inputs": [{"internalType": "uint256", "name": "epoch", "type": "uint256"},
                                  {"internalType": "address", "name": "user", "type": "address"}], "name": "Claimable",
                       "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "view",
                       "type": "function"},


                   {"inputs": [], "name": "IsPaused", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                    "stateMutability": "view", "type": "function"},



                   {"inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "name": "Rounds",
                    "outputs": [{"internalType": "uint256", "name": "epoch", "type": "uint256"},
                                {"internalType": "uint256", "name": "bullAmount", "type": "uint256"},
                                {"internalType": "uint256", "name": "bearAmount", "type": "uint256"},
                                {"internalType": "uint256", "name": "rewardBaseCalAmount", "type": "uint256"},
                                {"internalType": "uint256", "name": "rewardAmount", "type": "uint256"},
                                {"internalType": "int256", "name": "lockPrice", "type": "int256"},
                                {"internalType": "int256", "name": "closePrice", "type": "int256"},
                                {"internalType": "uint32", "name": "startTimestamp", "type": "uint32"},
                                {"internalType": "uint32", "name": "lockTimestamp", "type": "uint32"},
                                {"internalType": "uint32", "name": "closeTimestamp", "type": "uint32"},
                                {"internalType": "uint32", "name": "lockPriceTimestamp", "type": "uint32"},
                                {"internalType": "uint32", "name": "closePriceTimestamp", "type": "uint32"},
                                {"internalType": "bool", "name": "closed", "type": "bool"},
                                {"internalType": "bool", "name": "canceled", "type": "bool"}],
                    "stateMutability": "view", "type": "function"},


                   {"inputs": [], "name": "currentEpoch",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view",
                    "type": "function"},


                   {"inputs": [{"internalType": "uint256", "name": "epoch", "type": "uint256"}], "name": "user_BetBear",
                    "outputs": [], "stateMutability": "payable", "type": "function"},
                   {"inputs": [{"internalType": "uint256", "name": "epoch", "type": "uint256"}], "name": "user_BetBull",
                    "outputs": [], "stateMutability": "payable", "type": "function"},
                   {"inputs": [{"internalType": "uint256[]", "name": "epochs", "type": "uint256[]"}],
                    "name": "user_Claim", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]


def clean_terminal():
    if platform.system() == "Windows":
        subprocess.Popen("cls", shell=True).communicate()
    else:
        print("\033c", end="")


def header():
    print(f'{bcolors.HEADER}{33 * "="} MULTI-STRATEGY BOT {34 * "="}{bcolors.ENDC}')

    print(f'Welcome! '
          f'\nGood Luck! {64 * " "}Exit(Ctrl+c)')


def get_tax(txnhash, og):
    txnhash = txnhash.get('logs')
    txnhash = txnhash[0].get('data')
    profit = w3.toInt(hexstr=txnhash)
    tax = profit * (og / 100)
    tax = round(tax)
    return {"tax": tax, "profit": w3.fromWei(profit, "ether")}


def is_valid_address(address):
    try:
        w3.toChecksumAddress(address)
        return True
    except Exception:
        return False


def is_valid_key(key):
    try:
        from eth_account.messages import encode_defunct
        message = encode_defunct(text='sign')
        w3.eth.account.sign_message(message, private_key=key)
        return True
    except Exception as e:
        return False


def validation():
    print(f'{bcolors.HEADER}{37 * "="} SET ACCOUNT {37 * "="}{bcolors.ENDC}\n')
    print(f'{49 * " "}(leave blank to enter simulation mode)')

    while True:
        address = str(input(f'{bcolors.WARNING}Account address:{bcolors.ENDC} '))

        if address == '':
            print(f'{bcolors.OKCYAN} Simulation Mode')
            time.sleep(2)
            return {'address': '0x0000000000000000000000000000000000000000', 'key': '', 'simulation': True}
        if not is_valid_address(address):
            print(f'{bcolors.FAIL}Invalid address{bcolors.ENDC}')
            continue
        private_key = str(input(f'{bcolors.WARNING}Private key:{bcolors.ENDC} '))
        if not is_valid_key(private_key):
            print(f'{bcolors.FAIL}Invalid key{bcolors.ENDC}')
            continue
        break

    ADDRESS = Web3.toChecksumAddress(address)
    PRIVATE_KEY = str(private_key).lower()

    return {'address': ADDRESS, 'key': PRIVATE_KEY, 'simulation': False}


def menu():
    print(f'{bcolors.HEADER}{35 * "="} SELECT STRATEGY {35 * "="}{bcolors.ENDC}\n')

    sts = ''
    for st in strategy_numbers.list:
        sts += f'    {strategy_numbers.list[st]} ({st}) {(21 - len(strategy_numbers.list[st]))*" "}'
        if int(st) % 2 == 0:
            sts += '\n'

    print(sts)

    copy_player_address = ''
    while True:
        strategy_input = str(input(f'\n{bcolors.WARNING}Strategy Number (1-13):{bcolors.ENDC} '))
        if strategy_input.isnumeric():
            if int(strategy_input) != 8 and 1 <= int(strategy_input) <= 13:
                print(f'{bcolors.OKCYAN} {strategy_numbers.list[strategy_input]} selected{bcolors.ENDC}')

                if int(strategy_input) != 6:
                    is_inverted = str(input(f'{bcolors.WARNING}Invert it? (y/n): {bcolors.ENDC}'))
                    if is_inverted == 'y':
                        is_inverted = True
                        print(f'{bcolors.OKCYAN} Invert mode ON {bcolors.ENDC}')
                    else:
                        is_inverted = False
                        print(f'{bcolors.OKCYAN} Invert mode OFF{bcolors.ENDC}')
                else:
                    is_inverted = False

                print(f'{bcolors.OKCYAN} Betting: Percentage of account balance (1) / Fixed Amount (2){bcolors.ENDC}')

                bet_type = str(input(f'{bcolors.WARNING}Bet Type (1-2): {bcolors.ENDC}'))
                if bet_type == '2':
                    bet_amount = str(input(f'{bcolors.WARNING}Amount (BNB): {bcolors.ENDC}'))
                    btype = 'BNB'
                elif bet_type == '1':
                    bet_amount = str(input(f'{bcolors.WARNING}Percentage (0-100): {bcolors.ENDC}'))
                    btype = '%'
                else:
                    print(f'{bcolors.FAIL} Wrong value, try again{bcolors.ENDC}')
                    continue
                if is_number(bet_amount):
                    print(f'{bcolors.OKCYAN} {strategy_numbers.list[strategy_input]} strategy '
                          f'| Base Bet: {bet_amount} {btype}{bcolors.ENDC}\n')
                    break
                else:
                    print(f'{bcolors.FAIL} Invalid bet amount, try again{bcolors.ENDC}')
            elif strategy_input == strategy_numbers.copy_player:
                bet_type = '2'
                btype = 'BNB'
                is_inverted = False
                print(f'{bcolors.OKCYAN} {strategy_numbers.list[strategy_input]} selected{bcolors.ENDC}')
                copy_player_address = str(input(f'{bcolors.WARNING}Copy player address:{bcolors.ENDC} '))
                if is_valid_address(copy_player_address):
                    print(f'{bcolors.OKCYAN} Copying {copy_player_address} %')
                    bet_amount = str(
                        input(f'{bcolors.WARNING}Bet Factor (bet_amount = copyplayer_bet_amount / bet_factor):'
                              f' {bcolors.ENDC}'))
                    if is_number(bet_amount):

                        print(f'{bcolors.OKCYAN} {strategy_numbers.list[strategy_input]} strategy '
                              f'| Bet Factor: {bet_amount} {bcolors.ENDC}\n')
                        break
                    else:
                        print(f'{bcolors.FAIL} Invalid bet factor, try again')
                        continue
                else:
                    print(f'{bcolors.FAIL} Invalid address, try again')
                    continue
            else:
                print(f'{bcolors.FAIL} Unknown command, try again')
                continue
        else:
            print(f'{bcolors.FAIL} Unknown command, try again')
            continue

    return {'strategy': strategy_input, 'bet_type': bet_type, 'bet_amount': bet_amount,
            'copy_player_address': copy_player_address, 'is_inverted': is_inverted}


def get_settings():
    settings = {
        'SECONDS_LEFT': 10,
        'GAS': 400000,
        'GAS_PRICE': 5100000000,
    }
    while True:
        print(f'{bcolors.OKCYAN} Choose seconds left to place bets before round locks:{bcolors.ENDC}')
        seconds_left = str(input(f'{bcolors.WARNING}(Default: 10) Set seconds:{bcolors.ENDC} '))
        if is_number(seconds_left):
            if 3 < float(seconds_left):
                settings['SECONDS_LEFT'] = float(seconds_left)
                print(f'{bcolors.OKCYAN} Betting at {seconds_left} seconds left before round lock{bcolors.ENDC}')
                break

            else:
                print(f'{bcolors.FAIL} Try a number between higher then 3{bcolors.ENDC}')
                continue

        elif seconds_left == '':
            print(f'{bcolors.OKCYAN} Default{bcolors.ENDC}')
            print(f'{bcolors.OKCYAN} Betting at 10 seconds left before round lock{bcolors.ENDC}')
            break
        else:
            print(f'{bcolors.FAIL} Try a number higher then 3{bcolors.ENDC}')
            continue

    return settings


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def time_left_to(bet_time):
    sleep_secs = (bet_time - dt.datetime.now()).total_seconds()
    if sleep_secs >= 0:
        time.sleep(sleep_secs)


def manual_header():
    print(f'{bcolors.OKCYAN} Go Bull ({options.go_bull}) | Go Bear ({options.go_bear}) | Change Base Bet (value) '
          f'| Restart ({options.restart})'
          f' | Do nothing to skip{bcolors.ENDC}')


def non_manual_header():
    print(f'{bcolors.OKCYAN} Skip ({options.skip}) | Change Base Bet (value) | Go Manual ({options.go_manual}) |'
          f' Restart ({options.restart}) | Do nothing to continue{bcolors.ENDC}')


def copy_player_header():
    print(f'{bcolors.OKCYAN} Skip ({options.skip}) | Change Factor (value) | Go Manual ({options.go_manual}) |'
          f' Restart ({options.restart}) | Do nothing to continue{bcolors.ENDC}')


def dapp():
    print(f'{bcolors.HEADER}{37 * "="} SELECT DAPP {37 * "="}{bcolors.ENDC}\n')
    print(f'       '
          f'       '
          f'        '
          f'     {dapps.list[dapps.pancake]} ({dapps.pancake})  |  {dapps.list[dapps.dogebets]} ({dapps.dogebets})'
          f' ')

    while True:
        dapp_input = str(input(f'{bcolors.WARNING}Dapp number (1-2):{bcolors.ENDC} '))
        if dapp_input.isnumeric():
            if 1 <= int(dapp_input) <= 2:
                print(f'{bcolors.OKCYAN} {dapps.list[dapp_input]} selected{bcolors.ENDC}')
                break
        else:
            print(f'{bcolors.FAIL} Unknown command, try again')
            continue
    return dapp_input


def node():
    print(f'{bcolors.HEADER}{37 * "="}  SET  NODE  {37 * "="}{bcolors.ENDC}\n')
    print(f'(leave blank for default public node)')

    node_input = str(input(f'{bcolors.WARNING}Node endpoint:{bcolors.ENDC} '))
    if node_input == '':
        node_input = 'https://bsc-dataseed1.defibit.io/'

    return node_input
