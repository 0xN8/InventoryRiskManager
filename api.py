from config import url, test_url
import time



url += "/info"



def post_user_spot_tokens(address, info):
    user_state = info.spot_user_state(address)
  
    print("User Balances: ", user_state['balances'])
    return user_state["balances"]



def post_user_futures_summary(address, info):
    user_state = info.user_state(address)

    print("User Futures Summary: ", user_state['assetPositions'])
    return user_state['assetPositions']

def allMids(info, hedge_coin, coin):
    mids = info.all_mids()

    if coin == None:
        hedge_mid = float(mids.get(hedge_coin))
        return hedge_mid
    else: 
        hedge_mid = float(mids.get(hedge_coin))
        coin_mid = float(mids.get(coin))
        return hedge_mid, coin_mid 

def candles_snapshot(info, hedge_coin, spot_coin, interval):
    end = int(time.time() * 1000)
    start = end - (1000 * 60 * 60 * 24 * 30)
    hedge_candles = info.candles_snapshot(hedge_coin, interval, start, end)
    spot_candles = info.candles_snapshot(spot_coin, interval, start, end)

    return hedge_candles, spot_candles

