from termcolor import cprint
from tools.api import allMids

def futuresOrder(hyperClass, hedgeCoin, isBuy, qty, px, reduceOnly):


    orderResult = hyperClass.exchange.order(hedgeCoin, isBuy, float(qty), float(px), {"limit": {"tif": "Alo"}}, reduceOnly)
    if orderResult["status"] == "ok":
        status = orderResult["response"]["data"]["statuses"][0]
        if 'error' in status:
            errorMessage = status['error']
            cprint(f"Error Message: {errorMessage}", 'white', 'on_red')
            while('Post only order would have immediately matched' in errorMessage):
                print("Trying to resubmit order...")
                hedgeMid = allMids(hyperClass, hedgeCoin, None)
                orderResult = hyperClass.exchange.order(hedgeCoin, isBuy, float(qty), float(hedgeMid), {"limit": {"tif": "Alo"}}, reduceOnly)
                status = orderResult["response"]["data"]["statuses"][0]
                if 'error' in status:
                    errorMessage = status['error']
                else:
                    break
        else:
            cprint(f"Order Status: {status}",'light_yellow', 'on_magenta')
            return
        
        cprint(f"Order resubmission attempt: {orderResult}", 'light_yellow', 'on_magenta')



def updateLeverage(hyperClass, coin, lev, isCross):
    # Update Leverage
    leverageResult = hyperClass.exchange.update_leverage(lev, coin, isCross)

    if leverageResult["status"] == "ok":
        cprint(f"Leverage Updated: {lev}", 'light_yellow', 'on_magenta')
    else:
        cprint(f"Leverage not updated: {leverageResult}", 'white', 'on_red')



def marketClose(hyperClass, coin):
    closeResult = hyperClass.exchange.market_close(coin)
    print(closeResult)


def closeOpenOrders(hyperClass, coin):

    cancelOrders = []
    openOrders = hyperClass.info.open_orders(hyperClass.hedgeAddress)
    if len(openOrders) == 0:
        return
    
    
    for order in openOrders:
        if order["coin"] == coin:
            cancelOrders.append({"coin": coin, "oid": order["oid"]})

    cancelStatus = hyperClass.exchange.bulk_cancel(cancelOrders)

    if cancelStatus["status"] == "ok":
        response = cancelStatus["response"]
        cprint(f"Order Cancelled: {response}", 'light_yellow', 'on_magenta')
    else:
        cprint(f"Orders not cancelled: {cancelStatus}", 'white', 'on_red')
  