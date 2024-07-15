from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from eth_account.signers.local import LocalAccount
from tools.env import get_env
import eth_account


def parseParameters(parameters, prod):
    for parameter in parameters:
        if parameter['Name'] == '/Inventory-Risk-Manager/dev/api' and not prod:
            apiKey = parameter['Value']
        elif parameter['Name'] == '/Inventory-Risk-Manager/prod/api' and prod:
            apiKey = parameter['Value']
        elif parameter['Name'] == '/HyperLiquid/prod/account-address':
            accAddress = parameter['Value']
        elif parameter['Name'] == '/HyperLiquid/prod/neu-address':
            neuAddress = parameter['Value']
    return apiKey, accAddress, neuAddress


def setup(url, prod):
    parameters = get_env()
    apiKey, accAddress, neuAddress = parseParameters(parameters, prod)
    account: LocalAccount = eth_account.Account.from_key(apiKey)
    info = Info(url, skip_ws= True)
    exchange = Exchange(account, url, vault_address=neuAddress)


    # Set address to the api address if no wallet is provided
    if accAddress == "":
        accAddress = account.address

    return account, accAddress, neuAddress, info, exchange


# def elapsed_time():
#     while True:
#         start_time = time.time() * 1000
#         elapsed_time = time.time()*1000 - start_time

#         print(f"Elapsed time: {elapsed_time} ms")