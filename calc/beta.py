from tools.api import candlesSnapshot
import numpy as np
from termcolor import cprint
import time


def calcReturns(candles):
    candleReturns = []
    for candle in candles:
        candleReturns.append((float(candle['c']) - float(candle['o'])) / float(candle['o']))
    return candleReturns


#Where the spot coins covariance is the first element in the beta calc
#second is the variance of the hedge coin
# so a value of > 1 means the coin is more volatile than the hedge coin
# a value of < 1 means the coin is less volatile than the hedge coin

def beta(hyperClass, hedgeCoin, coin):
    hedgeCandles, spotCandles = candlesSnapshot(hyperClass, hedgeCoin, coin, "5m", 144) # Beta for the last 12 hours
    hedgeReturns = calcReturns(hedgeCandles)
    spotReturns = calcReturns(spotCandles)

    if len(hedgeReturns) != len(spotReturns):
        if len(hedgeReturns) > len(spotReturns):
            len_diff = len(hedgeReturns) - len(spotReturns)
            hedgeReturns = hedgeReturns[+lenDiff:]
        elif len(spotReturns) > len(hedgeReturns):
            lenDiff = len(spotReturns) - len(hedgeReturns)
            spotReturns = spotReturns[+lenDiff:]

    covMatrix = np.cov(spotReturns, hedgeReturns)
    covSH = covMatrix[0][1]
    varH = np.var(hedgeReturns)

    betaVal = covSH / varH    

    return betaVal



def betaScanner(hyperClass, coin):
    meta = hyperClass.info.meta_and_asset_ctxs()
    coins = meta[0]['universe']
    ctxs = meta[1]
    
    

    coinCtxsList = [
        {
            "coin": coin['name'],
            "szDecimals": coin['szDecimals'],
            "maxLeverage": coin['maxLeverage'],
            "funding": ctx['funding'],
            "dayNtlVlm": ctx['dayNtlVlm'],
            "impactPxs": ctx['impactPxs']
        }
        for coin, ctx in zip(coins, ctxs) if float(ctx['dayNtlVlm']) > 200000
    ]
    
    print("Coin Contexts List Created")
    betaThreshold = 0
    bestBeta = {}

    for coinCtx in coinCtxsList:
        betaVal = beta(hyperClass, coinCtx['coin'], coin)
        if betaVal > betaThreshold:
            betaThreshold = betaVal
            bestBeta = coinCtx.copy()
            bestBeta['beta'] = betaVal

    cprint(f'Best Beta is: {bestBeta}', 'light_yellow', 'on_magenta')

    return bestBeta