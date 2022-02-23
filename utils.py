import datetime as dt
import platform
import subprocess
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware

w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org/'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


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

    list = {
        '1': 'AutoTrend',
        '2': 'UpTrend',
        '3': 'DownTrend',
        '4': 'HigherPayout',
        '5': 'LowerPayout',
        '6': 'Manual',
        '7': 'Random',
        '8': 'CopyPlayer',
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
    tax = profit * (og/100)
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
        print(e)
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

    print(f'       AutoTrend ({strategy_numbers.auto_trend})     |  UpTrend ({strategy_numbers.up_trend})'
          f'      |  DownTrend ({strategy_numbers.down_trend})  |  Random ({strategy_numbers.random})\n'
          f'       HigherPayout ({strategy_numbers.higher_payout})  |  LowerPayout ({strategy_numbers.lower_payout})  '
          f'|  Manual ({strategy_numbers.manual})     |  CopyPlayer ({strategy_numbers.copy_player})\n')

    copy_player_address = ''
    while True:
        strategy_input = str(input(f'{bcolors.WARNING}Strategy Number (1-8):{bcolors.ENDC} '))
        if strategy_input.isnumeric():
            if 1 <= int(strategy_input) <= 7:
                print(f'{bcolors.OKCYAN} {strategy_numbers.list[strategy_input]} selected{bcolors.ENDC}')

                bet_amount = str(input(f'{bcolors.WARNING}Base Bet (BNB): {bcolors.ENDC}'))
                if is_number(bet_amount):
                    print(f'{bcolors.OKCYAN} Starting {strategy_numbers.list[strategy_input]} strategy '
                          f'| Base Bet: {bet_amount} BNB{bcolors.ENDC}\n')
                    break
                else:
                    print(f'{bcolors.FAIL} Invalid bet amount, try again')
            elif strategy_input == strategy_numbers.copy_player:
                print(f'{bcolors.OKCYAN} {strategy_numbers.list[strategy_input]} selected{bcolors.ENDC}')
                copy_player_address = str(input(f'{bcolors.WARNING}Copy player address:{bcolors.ENDC} '))
                if is_valid_address(copy_player_address):
                    print(f'{bcolors.OKCYAN} Copying {copy_player_address} %')
                    bet_amount = str(input(f'{bcolors.WARNING}Bet Factor (bet_amount = copyplayer_bet_amount / bet_factor):'
                                           f' {bcolors.ENDC}'))
                    if is_number(bet_amount):

                        print(f'{bcolors.OKCYAN} Starting {strategy_numbers.list[strategy_input]} strategy '
                              f'| Bet Factor: {bet_amount} BNB{bcolors.ENDC}\n')
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

    return {'strategy': strategy_input, 'bet_amount': bet_amount, 'copy_player_address': copy_player_address}


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def time_left_to(bet_time):
    time.sleep((bet_time - dt.datetime.now()).total_seconds())


def manual_header():
    print(f'{bcolors.OKCYAN} Go Bull ({options.go_bull}) | Go Bear ({options.go_bear}) | Change Amount (BNB) '
          f'| Restart ({options.restart})'
          f' | Do nothing to skip{bcolors.ENDC}')


def non_manual_header():
    print(f'{bcolors.OKCYAN} Skip ({options.skip}) | Change Amount (BNB) | Go Manual ({options.go_manual}) |'
          f' Restart ({options.restart}) | Do nothing to continue{bcolors.ENDC}')


def copy_player_header():
    print(f'{bcolors.OKCYAN} Skip ({options.skip}) | Change Factor (value) | Go Manual ({options.go_manual}) |'
          f' Restart ({options.restart}) | Do nothing to continue{bcolors.ENDC}')
