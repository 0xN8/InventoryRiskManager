from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from eth_account.signers.local import LocalAccount
from dotenv import load_dotenv
import os, eth_account


def setup(url):
    load_dotenv()
    priv_key = os.getenv('api_priv_key')
    account: LocalAccount = eth_account.Account.from_key(priv_key)
    address = os.getenv('sub_address')
    track_address = os.getenv('track_address')
    info = Info(url, skip_ws= True)
    exchange = Exchange(account, url, vault_address=address)


    # Set address to the api address if no wallet is provided
    if address == "":
        address = account.address

    return account, address, track_address, info, exchange


# def elapsed_time():
#     while True:
#         start_time = time.time() * 1000
#         elapsed_time = time.time()*1000 - start_time

#         print(f"Elapsed time: {elapsed_time} ms")