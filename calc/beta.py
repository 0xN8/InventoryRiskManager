from tools.api import candlesSnapshot
from termcolor import cprint
from decimal import Decimal
import numpy as np



def calcReturns(candles):
    candleReturns = []
    for candle in candles:
        candleReturns.append((Decimal(candle['c']) - Decimal(candle['o'])) / Decimal(candle['o']))
    return candleReturns


#Where the spot coins covariance is the first element in the beta calc
#second is the variance of the hedge coin
# so a value of > 1 means the spot coin is more volatile than the hedge coin
# a value of < 1 means the spot coin is less volatile than the hedge coin

def beta(hyperClass, hedgeCoin, spotReturns):
    hedgeCandles = candlesSnapshot(hyperClass, hedgeCoin, "15m", 48) # Beta for the last 12 hours
    hedgeReturns = calcReturns(hedgeCandles)

    # if len(hedgeReturns) != len(spotReturns):
    #     if len(hedgeReturns) > len(spotReturns):
    #         len_diff = len(hedgeReturns) - len(spotReturns)
    #         hedgeReturns = hedgeReturns[lenDiff:]
    #     elif len(spotReturns) > len(hedgeReturns):
    #         lenDiff = len(spotReturns) - len(hedgeReturns)
    #         spotReturns = spotReturns[lenDiff:]

    covMatrix = np.cov(spotReturns, hedgeReturns)
    covSH = covMatrix[0][1]
    varH = np.var(hedgeReturns)

    betaVal = covSH / varH    

    return betaVal



def betaScanner(hyperClass, coin):
    meta = hyperClass.info.meta_and_asset_ctxs()
    coins = meta[0]['universe']
    ctxs = meta[1]
    
    
    #Create a list of coin contexts with a daily notional volume greater than 200,000
    coinCtxsList = [
        {
            "coin": coin['name'],
            "szDecimals": coin['szDecimals'],
            "maxLeverage": coin['maxLeverage'],
            "funding": ctx['funding'],
            "dayNtlVlm": ctx['dayNtlVlm'],
            "impactPxs": ctx['impactPxs']
        }
        for coin, ctx in zip(coins, ctxs) if Decimal(ctx['dayNtlVlm']) > 200000
    ]
    
    cprint("Coin Contexts List Created","light_cyan", "dark_grey")
    betaThreshold = 0
    bestBeta = {}
    spotCandles = candlesSnapshot(hyperClass, coin, "5m", 144)
    spotReturns = calcReturns(spotCandles)

    for coinCtx in coinCtxsList:
        betaVal = beta(hyperClass, coinCtx['coin'], spotReturns)
        if betaVal > betaThreshold:
            betaThreshold = betaVal
            bestBeta = coinCtx.copy()
            bestBeta['beta'] = betaVal

    cprint(f'Best Beta is: {bestBeta}', 'light_yellow', 'on_magenta')

    return bestBeta