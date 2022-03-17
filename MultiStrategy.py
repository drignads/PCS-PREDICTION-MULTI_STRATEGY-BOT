from prediction import Prediction
from strategies import Strategies
from inputimeout import inputimeout, TimeoutOccurred
from utils import *


def make_bet(epoch, strategy_number, bet_amount, bet_type, is_inverted, **kwargs):
    if bet_type == '1':
        balance = pr.w3.fromWei(
            pr.w3.eth.getBalance(account['address']), 'ether')
        bet_amount = (float(balance) * float(bet_amount)) / 100

    if strategy_number == strategy_numbers.manual:
        position = kwargs.get('position')
    elif strategy_number == strategy_numbers.copy_player:
        cp_player = strategy.call[strategy_number](epoch, kwargs.get('player'), 15, bet_amount)
        position = cp_player[0]
        bet_amount = w3.fromWei(cp_player[1], 'ether')
    else:
        position = strategy.call[strategy_number](5, 'BNBUSD', epoch)

    if is_inverted and position == 'bull':
        position = 'bear'
        invert = 'ON'
    elif is_inverted and position == 'bear':
        position = 'bull'
        invert = 'ON'
    elif not is_inverted:
        invert = 'OFF'
    else:
        invert = 'ON'

    if position == 'bull':
        if kwargs.get('simulation'):
            print(f'{bcolors.OKGREEN} Going {position} #{epoch} | {bet_amount} BNB -'
                  f' {bcolors.OKCYAN}SIMULATION MODE - Inverted: {invert} %{bcolors.ENDC}')
        else:
            print(f'{bcolors.OKGREEN} Going {position} #{epoch} | {bet_amount} BNB - Inverted: {invert} %{bcolors.ENDC}')
            txn = pr.bet_bull(bet_amount, epoch, gas=settings['GAS'], gas_price=settings['GAS_PRICE'])
            print(f' https://bscscan.com/tx/{txn.get("transactionHash").hex()}')
    elif position == 'bear':
        if kwargs.get('simulation'):
            print(f'{bcolors.OKGREEN} Going {position} #{epoch} | {bet_amount} BNB -'
                  f' {bcolors.OKCYAN}SIMULATION MODE - Inverted: {invert} %{bcolors.ENDC}')
        else:
            print(f'{bcolors.OKGREEN} Going {position} #{epoch} | {bet_amount} BNB - Inverted: {invert} %{bcolors.ENDC}')
            txn = pr.bet_bear(bet_amount, epoch, gas=settings['GAS'], gas_price=settings['GAS_PRICE'])
            print(f' https://bscscan.com/tx/{txn.get("transactionHash").hex()}')
    else:
        if kwargs.get('simulation'):
            print(f' {strategy_numbers.list[strategy_number]}{bcolors.OKCYAN} skipped # {epoch} -'
                  f' {bcolors.OKCYAN}SIMULATION MODE - Inverted: {invert} %{bcolors.ENDC}')
        else:
            print(f' {strategy_numbers.list[strategy_number]}{bcolors.OKCYAN} skipped #{epoch} - Inverted: {invert}{bcolors.ENDC}')


def run():
    strategy_number = strategy_settings['strategy']
    base_bet = strategy_settings['bet_amount']
    bet_type = strategy_settings['bet_type']
    simulation = account['simulation']
    copy_player_address = strategy_settings['copy_player_address']
    bet_amount = base_bet
    is_inverted = strategy_settings['is_inverted']

    current_round = pr.new_round(settings['SECONDS_LEFT'], strategy_numbers.list[strategy_number], base_bet, bet_type)
    is_playing = True
    while True:
        try:
            now = dt.datetime.now()
            if now >= (current_round['bet_time'] - dt.timedelta(seconds=300)):
                timeout = (current_round['bet_time'] - now).total_seconds()
                if strategy_number == strategy_numbers.manual:
                    manual_header()
                    try:
                        user_input = inputimeout(prompt=f'{bcolors.WARNING}$:{bcolors.ENDC} ', timeout=timeout)
                        if user_input == options.go_bull:
                            make_bet(current_round["current_epoch"], strategy_number, bet_amount, bet_type, False,
                                     position='bull',
                                     simulation=simulation)
                            time_left_to(current_round['bet_time'])
                            is_playing = False
                        elif user_input == options.go_bear:
                            make_bet(current_round["current_epoch"], strategy_number, bet_amount, bet_type, False
                                     ,position='bear',
                                     simulation=simulation)
                            time_left_to(current_round['bet_time'])
                            is_playing = False
                        elif user_input == options.restart:
                            break
                        elif is_number(user_input):
                            bet_amount = float(user_input)
                            print(f'{bcolors.OKCYAN} Amount changed to {bet_amount}{bcolors.ENDC}')
                            continue
                        else:
                            print(f'{bcolors.FAIL} Unknown command, try again...{bcolors.ENDC}')
                            continue
                    except TimeoutOccurred:
                        print(f'{bcolors.OKCYAN} Skipping #{current_round["current_epoch"]} %{bcolors.ENDC}')
                        is_playing = False
                        pass
                else:
                    if strategy_number == strategy_numbers.copy_player:
                        copy_player_header()
                    else:
                        non_manual_header()
                    try:
                        user_input = inputimeout(prompt=f'{bcolors.WARNING}$:{bcolors.ENDC} ', timeout=timeout)
                        if user_input == options.skip:
                            is_playing = False
                            print(f'{bcolors.OKCYAN} Skipping #{current_round["current_epoch"]} %{bcolors.ENDC}')
                            time_left_to(current_round['bet_time'])
                        elif user_input == options.restart:
                            break
                        elif user_input == options.go_manual:
                            print(f'{bcolors.OKCYAN} Going manual...%{bcolors.ENDC}')
                            strategy_number = strategy_numbers.manual
                            continue
                        elif is_number(user_input):
                            bet_amount = float(user_input)
                            if strategy_number == strategy_numbers.copy_player:
                                print(f'{bcolors.OKCYAN} Factor changed to {bet_amount}{bcolors.ENDC}')
                            else:
                                print(f'{bcolors.OKCYAN} Base Bet changed to {bet_amount}{bcolors.ENDC}')
                            continue
                        else:
                            print(f'{bcolors.FAIL} Unknown command, try again...{bcolors.ENDC}')
                            continue
                    except TimeoutOccurred:
                        pass

                if is_playing:
                    if strategy_number == strategy_numbers.copy_player:
                        make_bet(current_round["current_epoch"], strategy_number, bet_amount, bet_type, is_inverted,
                                 player=copy_player_address, simulation=simulation)
                        pr.close_round(current_round["current_epoch"], partner=copy_player_address, simulation=simulation)
                    else:
                        make_bet(current_round["current_epoch"], strategy_number, bet_amount, bet_type, is_inverted,
                                 simulation=simulation)
                        pr.close_round(current_round["current_epoch"], simulation=simulation)
                else:
                    is_playing = True
                    pr.close_round(current_round["current_epoch"], simulation=simulation)

                current_round = pr.new_round(settings['SECONDS_LEFT'], strategy_numbers.list[strategy_number],
                                             bet_amount, bet_type)
        except Exception as error:
            print(f'{bcolors.FAIL}Restarting...% Error: {error}{bcolors.ENDC}')
            current_round = pr.new_round(settings['SECONDS_LEFT'], strategy_numbers.list[strategy_number], bet_amount,
                                         bet_type)


if __name__ == '__main__':
    is_auth = False
    clean_terminal()
    while True:
        if not is_auth:
            header()
            dapp = dapp()
            node = node()
            account = validation()
            try:
                pr = Prediction(account['address'], account['key'], dapp, node)
            except Exception:
                pr = Prediction(account['address'], account['key'], dapp, 'https://bsc-dataseed1.binance.org/')
            strategy = Strategies(pr)
            clean_terminal()
            is_auth = True
        header()
        strategy_settings = menu()
        settings = get_settings()
        run()
