from trading.futures import futuresOrder, updateLeverage, closeOpenOrders
from tools.api import postUserSpotTokens, postUserFuturesSummary, allMids, candlesSnapshot
from termcolor import cprint
import time

def trade(hyperClass, coin, bestBeta, coinShort):

    while True:
        time.sleep(40) # default 0.4; 1 loop without delay ~ 600 ms
                        #16 req/loop * 60 loop/min = 960 w/m < 1200 weigh/min limit
        spotBalances = postUserSpotTokens(hyperClass) #todo: listen with websockets for spot balance changes
        futuresPositions = postUserFuturesSummary(hyperClass) 
        futuresValue = 0
        spotSize = 0
        leverage = bestBeta['beta'] if bestBeta['beta'] <= bestBeta['maxLeverage'] else bestBeta['maxLeverage']


        #Do we already carry a position in the hedge coin?
        for position in futuresPositions:
            if position["position"]['coin'] == bestBeta["coin"]:
                futuresValue = float(position["position"]['positionValue'])
                futuresSize = float(position["position"]['szi'])
                break
 
        #Do we have a balance in the spot market of our market made coin (short name)?
        for balance in spotBalances:
            if balance["coin"] == coinShort:
                spotSize = float(balance["total"])
                break

        # if leverage == 0:
        #     cprint("Beta is set to 0, skipping trade", 'white', 'on_red')
        #     continue


        futuresPx, spotPx = allMids(hyperClass, bestBeta['coin'], coin) #todo: listen with websockets for mid price changes; will give most up to date price
        spotValue = spotSize * spotPx


        cprint(f"Spot Value: {spotValue}", 'light_green', 'on_blue')
        cprint(f"Futures Value: {futuresValue}", 'light_green', 'on_blue')

        if futuresValue  > 1.1 * leverage * spotValue:
            # Update Leverage
            if leverage > 1:
                updateLeverage(hyperClass, bestBeta['coin'], round(leverage), False)

            qty = round((futuresValue - leverage * spotValue) / futuresPx, bestBeta['szDecimals'])
            cprint(f"Qty: {qty}", 'light_green', 'on_blue')
            cprint(f"Px: {futuresPx}", 'light_green', 'on_blue')
            #cancel all open orders and submit new order
            closeOpenOrders(hyperClass, bestBeta['coin'])
            futuresOrder(hyperClass, bestBeta['coin'], True, qty, int(futuresPx)-1, True)

    
        elif futuresValue < 0.9 * leverage * spotValue:
            # Update Leverage
            if leverage > 1:
                updateLeverage(hyperClass, bestBeta['coin'], round(leverage), False)

            qty = round((leverage * spotValue - futuresValue) / futuresPx, bestBeta['szDecimals'])
            cprint(f"Qty: {qty}", 'light_green', 'on_blue')
            cprint(f"Px: {futuresPx}", 'light_green', 'on_blue')
            #cancel all open orders and submit new order
            closeOpenOrders(hyperClass, bestBeta['coin'])
            futuresOrder(hyperClass, bestBeta['coin'], False, qty, int(futuresPx)+1, False)

