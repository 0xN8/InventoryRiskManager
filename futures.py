from termcolor import cprint
from api import allMids

def futures_order(exchange, hedge_coin, is_buy, qty, px, reduce_only, info):


    order_result = exchange.order(hedge_coin, is_buy, qty, px, {"limit": {"tif": "Alo"}}, reduce_only)
    if order_result["status"] == "ok":
        status = order_result["response"]["data"]["statuses"][0]
        if 'error' in status:
            error_message = status['error']
            cprint(f"Error Message: {error_message}", 'white', 'on_red')
            while('Post only order would have immediately matched' in error_message):
                print("Trying to resubmit order...")
                hedge_mid = allMids(info, hedge_coin, None)
                order_result = exchange.order(hedge_coin, is_buy, qty, int(hedge_mid)-1 if is_buy else int(hedge_mid)+1, {"limit": {"tif": "Alo"}}, reduce_only)
                status = order_result["response"]["data"]["statuses"][0]
                if 'error' in status:
                    error_message = status['error']
                else:
                    break
        else:
            cprint(f"Order Status: {status}",'light_yellow', 'on_magenta')
            return
        
        cprint(f"Order resubmission attempt: {order_result}", 'light_yellow', 'on_magenta')



def update_leverage(exchange, coin, lev, is_cross):
    # Update Leverage
    leverage_result = exchange.update_leverage(lev, coin, is_cross)

    if leverage_result["status"] == "ok":
        cprint(f"Leverage Updated: {lev}", 'light_yellow', 'on_magenta')
    else:
        cprint(f"Leverage not updated: {leverage_result}", 'white', 'on_red')



def market_close(exchange, coin):
    close_result = exchange.market_close(coin)
    print(close_result)


def close_open_orders(exchange, info, address, coin):

    cancel_orders = []
    open_orders = info.open_orders(address)
    if len(open_orders) == 0:
        return
    
    
    for order in open_orders:
        if order["coin"] == coin:
            cancel_orders.append({"coin": coin, "oid": order["oid"]})

    cancel_status = exchange.bulk_cancel(cancel_orders)

    if cancel_status["status"] == "ok":
        response = cancel_status["response"]
        cprint(f"Order Cancelled: {response}", 'light_yellow', 'on_magenta')
    else:
        cprint(f"Orders not cancelled: {cancel_status}", 'white', 'on_red')
  