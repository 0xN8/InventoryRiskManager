from utils import setup
from config import url, coin, hedge_coin, test_url, coin_short
from trade import trade
from api import allMids




def main():
    account, acc_address, neu_address, info, exchange = setup(url, prod = True)
    trade(info, exchange, coin, hedge_coin, acc_address, neu_address, coin_short)
main()