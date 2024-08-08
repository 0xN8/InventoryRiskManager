import websocket, threading, json, time
from termcolor import cprint
from decimal import Decimal



def on_open(ws, msg):
    cprint(f"### opened ### {msg}", "magenta", "on_white")
    ws.send(json.dumps(msg))

def on_error(ws, error):
    cprint({error}, "white", "on_red")

def on_close(ws, *args):
    cprint(f"### closed ### {args}", "white", "on_red")
    cprint("WebSocket connection closed, attempting to reconnect...", "magenta", "on_white")
    time.sleep(3)  # wait for 3 seconds before attempting to reconnect
    reconnect(ws)



def reconnect(ws):
    while True:
        try:
            ws.run_forever()
        except Exception as e:
            cprint("Error while reconnecting, trying again in 3 seconds...", "white", "on_red")
            time.sleep(3)


def send_ping(ws):
    while True:
        time.sleep(55)
        ws.send(json.dumps({ "method": "ping" }))



def subscribe(args, callback, url):

    msg = {
        "method": "subscribe",
        "subscription": args
    }

    ws = websocket.WebSocketApp(url, on_message = callback, on_error = on_error, on_close = on_close)
    ws.on_open = lambda ws: on_open(ws, msg)
    ws.run_forever()

    

def heartbeatSub(args, callback, url):
    msg = {
        "method": "subscribe",
        "subscription": args
    }

    ws = websocket.WebSocketApp(url, on_message = callback, on_error = on_error, on_close = on_close)
    ws.on_open = lambda ws: ws.send(json.dumps(msg))
    heartbeat = threading.Thread(target = send_ping, args = (ws,),)
    heartbeat.start()
    ws.run_forever()




def postUserSpotTokens(hyperClass):
    userState = hyperClass.info.spot_user_state(hyperClass.makerAddress)
  
    print("User Balances: ", userState['balances'])
    return userState["balances"]



def postUserFuturesSummary(hyperClass):
    userState = hyperClass.info.user_state(hyperClass.hedgeAddress)

    print("User Futures Summary: ", userState['assetPositions'])
    return userState['assetPositions']



# def allMids(hyperClass, hedgeCoin, coin):
#     mids = hyperClass.info.all_mids()

#     if coin == None:
#         hedgeMid = Decimal(mids.get(hedgeCoin))
#         return hedgeMid
#     else: 
#         hedgeMid = Decimal(mids.get(hedgeCoin))
#         coinMid = Decimal(mids.get(coin))
#         return hedgeMid, coinMid
    

#candle snapshot in ascending order
def candlesSnapshot(hyperClass, coin, interval, lookback):
    end = int(time.time() * 1000)
    start = end - (1000 * 60 * 60 * 24 * 30) # 30 days ago as start time
    candles = hyperClass.info.candles_snapshot(coin, interval, start, end)

    candles = candles[-lookback:]
    

    return candles

