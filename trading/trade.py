from trading.futures import futuresOrder, updateLeverage, closeOpenOrders
from tools.config import coin, coinShort, wsUrl
from tools.api import postUserSpotTokens, postUserFuturesSummary, subscribe, heartbeatSub, candlesSnapshot
from termcolor import cprint
from decimal import Decimal
import collections, threading, json

spotBalance = collections.deque([0],maxlen=10)
futesValue = collections.deque([0],maxlen=10)
futesSize = collections.deque([0],maxlen=10)
hedgeCandles = collections.deque(maxlen=10)
spotCandles = collections.deque(maxlen=10)


def spotFillsSubCallback(ws, data):
    # cprint(f"Spot Fill Callback {data}", 'light_cyan', 'on_dark_grey')
    data= json.loads(data)

    if data['channel'] == 'subscriptionResponse':
        return

    if data['data'].get('isSnapshot') == True:
        return
    
    fills = data['data']['fills']

    for fill in fills:
        if fill['coin'] == coin:
            if fill['side'] == 'A':
                appendSz = -1*Decimal(fill['sz'])
                spotBalance.append(spotBalance[-1] + appendSz)
                cprint(f"Spot Balance -- {spotBalance[-1]}", 'light_green', 'on_blue')
                hedge()
            else:
                appendSz = Decimal(fill['sz']) - Decimal(fill['fee'])
                spotBalance.append(spotBalance[-1] + appendSz)
                cprint(f"Spot Balance -- {spotBalance[-1]}", 'light_green', 'on_blue')
                hedge()

    

def hedgeFillsSubCallback(ws, data):
    # cprint(f"Hedge Fill Callback {data}", 'light_cyan', 'on_dark_grey')
    data= json.loads(data)

    if data['channel'] == 'subscriptionResponse':
        return

    if data['data'].get('isSnapshot') == True:
        return
    
    fills = data['data']['fills']

    for fill in fills:
        if fill['coin'] == globalBestBeta['coin']:
            if fill['side'] == 'B':
                appendVal = -1*Decimal(fill['sz'])*Decimal(fill['px'])
                appendSz = -1*Decimal(fill['sz'])
                futesValue.append(futesValue[-1] + appendVal)
                futesSize.append(futesSize[-1] + appendSz)
                cprint(f"Futures Value: ${futesValue[-1]}", 'light_green', 'on_blue')
                cprint(f"Futures Size -- {futesSize[-1]}", 'light_green', 'on_blue')
            else:
                appendVal = Decimal(fill['sz'])*Decimal(fill['px'])
                appendSz = Decimal(fill['sz'])
                futesValue.append(futesValue[-1] + appendVal)
                futesSize.append(futesSize[-1] + appendSz)
                cprint(f"Futures Value: ${futesValue[-1]}", 'light_green', 'on_blue')
                cprint(f"Futures Size: -- {futesSize[-1]}", 'light_green', 'on_blue')



def hedgeCandleSubCallback(ws, data): #could replace this with l2Book data but shouldn't matter
    # cprint(f"Hedge Candle Callback {data}", 'light_cyan', 'on_dark_grey')
    data = json.loads(data)

    if data['channel'] == 'subscriptionResponse':
        return
    
    candle = data['data']

    if candle["T"] == hedgeCandles[-1]["T"]:
        hedgeCandles[-1] = candle
    else:
        hedgeCandles.append(candle)



def spotCandleSubCallback(ws, data):
    # cprint(f"Spot Candle Callback {data}", 'light_cyan', 'on_dark_grey')
    data = json.loads(data)

    if data['channel'] == 'subscriptionResponse':
        return
    
    candle = data['data']

    if candle["T"] == spotCandles[-1]["T"]:
        spotCandles[-1] = candle
    else:
        spotCandles.append(candle)



def hedge():
    cprint("Hedging...", 'light_cyan', 'on_dark_grey')
    cprint(f"Spot Current Value: ${spotBalance[-1] * Decimal(spotCandles[-1]['c'])}", 'light_green', 'on_blue')
    cprint(f"Futures Current Value: ${(futesValue[-1] - Decimal(hedgeCandles[-1]['c']) * futesSize[-1]) + futesValue[-1]}", 'light_green', 'on_blue')

    leverage = globalBestBeta['beta'] if globalBestBeta['beta'] <= globalBestBeta['maxLeverage'] else globalBestBeta['maxLeverage']
    excess = Decimal(1.2)
    shortage = Decimal(0.8)


    if (futesValue[-1] - Decimal(hedgeCandles[-1]["c"]) * futesSize[-1]) + futesValue[-1]  > excess * leverage * spotBalance[-1] * Decimal(spotCandles[-1]["c"]): #current futes value > 110% * beta * spot value
        # Update Leverage
        if leverage > 1:
            updateLeverage(globalHyperClass, globalBestBeta['coin'], round(leverage), False)

        qty = round((((futesValue[-1] - Decimal(hedgeCandles[-1]["c"])  * futesSize[-1]) + futesValue[-1]) - leverage * spotBalance[-1] * Decimal(spotCandles[-1]["c"])) / Decimal(hedgeCandles[-1]["c"]) , globalBestBeta['szDecimals']) #(current futes value - beta * spot value)/hedge price
        cprint(f"Qty to reduce: {qty}", 'light_green', 'on_blue')
        cprint(f"@ px: {hedgeCandles[-1]['c']}", 'light_green', 'on_blue')
        #cancel all open orders and submit new order
        closeOpenOrders(globalHyperClass, globalBestBeta['coin'])
        futuresOrder(globalHyperClass, globalBestBeta['coin'], True, qty, Decimal(hedgeCandles[-1]["c"]), True)


    elif (futesValue[-1] - Decimal(hedgeCandles[-1]["c"]) * futesSize[-1]) + futesValue[-1] < shortage * leverage * spotBalance[-1] * Decimal(spotCandles[-1]["c"]): #current futes value < 90% * beta * spot value
        # Update Leverage
        if leverage > 1:
            updateLeverage(globalHyperClass, globalBestBeta['coin'], round(leverage), False)

        qty = round((leverage * spotBalance[-1] * Decimal(spotCandles[-1]["c"]) - ((futesValue[-1] - Decimal(hedgeCandles[-1]["c"]) * futesSize[-1]) + futesValue[-1])) / Decimal(hedgeCandles[-1]["c"]), globalBestBeta['szDecimals']) #(current futes value - beta * spot value)/hedge price
        cprint(f"Qty to add: {qty}", 'light_green', 'on_blue')
        cprint(f"@ px: {hedgeCandles[-1]['c']}", 'light_green', 'on_blue')
        #cancel all open orders and submit new order
        closeOpenOrders(globalHyperClass, globalBestBeta['coin'])
        futuresOrder(globalHyperClass, globalBestBeta['coin'], False, qty, Decimal(hedgeCandles[-1]["c"]), False)





def hedge_thread(hyperClass, bestBeta):

    global globalHyperClass, globalBestBeta
    globalHyperClass = hyperClass
    globalBestBeta = bestBeta

    spotTokens = postUserSpotTokens(hyperClass)

    #Do we have a balance in the spot market of our market made coin (short name)?
    for token in spotTokens:
        if token["coin"] == coinShort:
            spotBalance.append(Decimal(token["total"]))
            break

    futesSummary = postUserFuturesSummary(hyperClass) 

    #Do we already carry a position in the hedge coin?
    for fute in futesSummary:
        if fute["position"]['coin'] == bestBeta["coin"]:
            futesValue.append(Decimal(fute["position"]['positionValue'])) #dollar value of position
            futesSize.append(Decimal(fute["position"]['szi'])*-1) #size of position
            break

    cprint(f"Spot Balance -- {spotBalance[-1]}", 'light_green', 'on_blue')
    cprint(f"Futures Value: ${futesValue[-1]}", 'light_green', 'on_blue')

    spotCandle = candlesSnapshot(hyperClass, coin, "5m", 1)
    hedgeCandle = candlesSnapshot(hyperClass, bestBeta["coin"], "5m", 1)

    spotCandles.append(spotCandle[0])
    hedgeCandles.append(hedgeCandle[0])


    spotFillsThread = threading.Thread(target = subscribe, args = ({"type": "userFills","user": hyperClass.makerAddress}, spotFillsSubCallback, wsUrl))
    hedgeFillsThread = threading.Thread(target = subscribe, args = ({"type": "userFills","user": hyperClass.hedgeAddress}, hedgeFillsSubCallback, wsUrl))
    hedgeCandlesThread = threading.Thread(target = subscribe, args = ({"type": "candle","coin": bestBeta["coin"],"interval": "5m"}, hedgeCandleSubCallback, wsUrl))
    spotCandlesThread = threading.Thread(target = subscribe, args = ({"type": "candle","coin": coin,"interval": "5m"}, spotCandleSubCallback, wsUrl))


    spotFillsThread.start()
    hedgeFillsThread.start()
    hedgeCandlesThread.start()
    spotCandlesThread.start()

    print("Spot Fills Thread Status: ", spotFillsThread.is_alive())
    print("Hedge Fills Thread Status: ", hedgeFillsThread.is_alive())
    print("Hedge Candles Thread Status: ", hedgeCandlesThread.is_alive())
    print("Spot Candles Thread Status: ", spotCandlesThread.is_alive())