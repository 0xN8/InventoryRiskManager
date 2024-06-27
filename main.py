from utils import setup
from config import url, coin, hedge_coin, test_url
from trade import trade
from api import allMids




def main():
    account, address, track_address, info, exchange = setup(url)
    trade(info, exchange, coin, hedge_coin, address, track_address)
main()