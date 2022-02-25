from prediction import Prediction
from strategies import Strategies
from inputimeout import inputimeout, TimeoutOccurred
from utils import *


def make_bet(epoch, strategy_number, bet_amount, **kwargs):
    if strategy_number == strategy_numbers.manual:
        position = kwargs.get('position')
    elif strategy_number == strategy_numbers.copy_player:
        cp_player = strategy.call[strategy_number](epoch, kwargs.get('player'), 15, bet_amount)
        position = cp_player[0]
        bet_amount = w3.fromWei(cp_player[1], 'ether')
    else:
        position = strategy.call[strategy_number](epoch)

    if position == 'bull':
        if kwargs.get('simulation'):
            print(f'{bcolors.OKGREEN} Going {position} #{epoch} | {bet_amount} BNB -'
                  f' {bcolors.OKCYAN}SIMULATION MODE %{bcolors.ENDC}')
        else:
            print(f'{bcolors.OKGREEN} Going {position} #{epoch} | {bet_amount} BNB  %{bcolors.ENDC}')
            txn = pr.bet_bull(bet_amount, epoch, gas=settings['GAS'], gas_price=settings['GAS_PRICE'])
            print(f' https://bscscan.com/tx/{txn.get("transactionHash").hex()}')

    elif position == 'bear':
        if kwargs.get('simulation'):
            print(f'{bcolors.OKGREEN} Going {position} #{epoch} | {bet_amount} BNB -'
                  f' {bcolors.OKCYAN}SIMULATION MODE %{bcolors.ENDC}')
        else:
            print(f'{bcolors.OKGREEN} Going {position} #{epoch} | {bet_amount} BNB  %{bcolors.ENDC}')
            txn = pr.bet_bear(bet_amount, epoch, gas=settings['GAS'], gas_price=settings['GAS_PRICE'])
            print(f' https://bscscan.com/tx/{txn.get("transactionHash").hex()}')

    else:
        if kwargs.get('simulation'):
            print(f' {strategy_numbers.list[strategy_number]}{bcolors.OKCYAN} skipped #{epoch}{bcolors.ENDC} -'
                  f' {bcolors.OKCYAN}SIMULATION MODE %{bcolors.ENDC}')
        else:
            print(f' {strategy_numbers.list[strategy_number]}{bcolors.OKCYAN} skipped #{epoch}{bcolors.ENDC}')


def run():
    strategy_number = strategy_settings['strategy']
    base_bet = strategy_settings['bet_amount']
    simulation = account['simulation']
    copy_player_address = strategy_settings['copy_player_address']
    bet_amount = base_bet

    current_round = pr.new_round(settings['SECONDS_LEFT'], strategy_numbers.list[strategy_number], base_bet)
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
                            make_bet(current_round["current_epoch"], strategy_number, bet_amount, position='bull',
                                     simulation=simulation)
                            time_left_to(current_round['bet_time'])
                            is_playing = False
                        elif user_input == options.go_bear:
                            make_bet(current_round["current_epoch"], strategy_number, bet_amount, position='bear',
                                     simulation=simulation)
                            time_left_to(current_round['bet_time'])
                            is_playing = False
                        elif user_input == options.restart:
                            break
                        elif is_number(user_input):
                            bet_amount = float(user_input)
                            print(f'{bcolors.OKCYAN} Amount changed to {bet_amount} BNB{bcolors.ENDC}')
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
                                print(f'{bcolors.OKCYAN} Amount changed to {bet_amount} BNB{bcolors.ENDC}')
                            continue
                        else:
                            print(f'{bcolors.FAIL} Unknown command, try again...{bcolors.ENDC}')
                            continue
                    except TimeoutOccurred:
                        pass

                if is_playing:
                    if strategy_number == strategy_numbers.copy_player:
                        make_bet(current_round["current_epoch"], strategy_number, bet_amount,
                                 player=copy_player_address, simulation=simulation)
                        pr.close_round(current_round["current_epoch"], partner=copy_player_address, simulation=simulation)
                    else:
                        make_bet(current_round["current_epoch"], strategy_number, bet_amount,
                                 simulation=simulation)
                        pr.close_round(current_round["current_epoch"], simulation=simulation)
                else:
                    is_playing = True
                    pr.close_round(current_round["current_epoch"], simulation=simulation)

                current_round = pr.new_round(settings['SECONDS_LEFT'], strategy_numbers.list[strategy_number],
                                             bet_amount)
        except Exception as error:
            print(f'{bcolors.FAIL}Restarting...% Error: {error}{bcolors.ENDC}')
            current_round = pr.new_round(settings['SECONDS_LEFT'], strategy_numbers.list[strategy_number], bet_amount)


if __name__ == '__main__':
    is_auth = False
    clean_terminal()
    while True:
        if not is_auth:
            header()
            dapp = dapp()
            account = validation()
            pr = Prediction(account['address'], account['key'], dapp)
            strategy = Strategies(pr)
            clean_terminal()
            is_auth = True
        header()
        strategy_settings = menu()
        settings = pr.get_settings()
        run()
