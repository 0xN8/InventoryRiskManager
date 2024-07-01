from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from eth_account.signers.local import LocalAccount
from env import get_env
import eth_account


def parse_parameters(parameters, prod):
    for parameter in parameters:
        if parameter['Name'] == '/Inventory-Risk-Manager/dev/api' and not prod:
            api_key = parameter['Value']
        elif parameter['Name'] == '/Inventory-Risk-Manager/prod/api' and prod:
            api_key = parameter['Value']
        elif parameter['Name'] == '/HyperLiquid/prod/account-address':
            acc_address = parameter['Value']
        elif parameter['Name'] == '/HyperLiquid/prod/neu-address':
            neu_address = parameter['Value']
    return api_key, acc_address, neu_address


def setup(url, prod):
    parameters = get_env()
    api_key, acc_address, neu_address = parse_parameters(parameters, prod)
    account: LocalAccount = eth_account.Account.from_key(api_key)
    info = Info(url, skip_ws= True)
    exchange = Exchange(account, url, vault_address=neu_address)


    # Set address to the api address if no wallet is provided
    if acc_address == "":
        acc_address = account.address

    return account, acc_address, neu_address, info, exchange


# def elapsed_time():
#     while True:
#         start_time = time.time() * 1000
#         elapsed_time = time.time()*1000 - start_time

#         print(f"Elapsed time: {elapsed_time} ms")