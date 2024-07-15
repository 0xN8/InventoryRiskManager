import time



def postUserSpotTokens(hyperClass):
    userState = hyperClass.info.spot_user_state(hyperClass.accAddress)
  
    print("User Balances: ", userState['balances'])
    return userState["balances"]



def postUserFuturesSummary(hyperClass):
    userState = hyperClass.info.user_state(hyperClass.neuAddress)

    print("User Futures Summary: ", userState['assetPositions'])
    return userState['assetPositions']

def allMids(hyperClass, hedgeCoin, coin):
    mids = hyperClass.info.all_mids()

    if coin == None:
        hedgeMid = float(mids.get(hedgeCoin))
        return hedgeMid
    else: 
        hedgeMid = float(mids.get(hedgeCoin))
        coinMid = float(mids.get(coin))
        return hedgeMid, coinMid 
    

#candle snapshot in ascending order
def candlesSnapshot(hyperClass, hedgeCoin, spotCoin, interval, lookback):
    end = int(time.time() * 1000)
    start = end - (1000 * 60 * 60 * 24 * 30)
    hedgeCandles = hyperClass.info.candles_snapshot(hedgeCoin, interval, start, end)
    spotCandles = hyperClass.info.candles_snapshot(spotCoin, interval, start, end)

    hedgeCandles = hedgeCandles[-lookback:]
    spotCandles = spotCandles[-lookback:]
    

    return hedgeCandles, spotCandles

