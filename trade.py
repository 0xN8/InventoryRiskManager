from futures import futures_order, update_leverage, close_open_orders
from api import post_user_spot_tokens, post_user_futures_summary, allMids, candles_snapshot
from termcolor import cprint
import numpy as np
import time


def calc_returns(candles):
    candle_returns = []
    for candle in candles:
        candle_returns.append((float(candle['c']) - float(candle['o'])) / float(candle['o']))
    return candle_returns


def beta(info, hedge_coin, coin):
    hedge_candles, spot_candles = candles_snapshot(info, hedge_coin, coin, "5m", 144)
    hedge_returns = calc_returns(hedge_candles)
    spot_returns = calc_returns(spot_candles)

    if len(hedge_returns) != len(spot_returns):
        if len(hedge_returns) > len(spot_returns):
            len_diff = len(hedge_returns) - len(spot_returns)
            hedge_returns = hedge_returns[+len_diff:]
        elif len(spot_returns) > len(hedge_returns):
            len_diff = len(spot_returns) - len(hedge_returns)
            spot_returns = spot_returns[+len_diff:]

    cov_matrix = np.cov(spot_returns, hedge_returns)
    cov_SH = cov_matrix[0][1]
    var_H = np.var(hedge_returns)

    beta_val = cov_SH / var_H
    cprint(f"Beta: {beta_val}", 'light_green', 'on_blue')

    beta_val = round(beta_val)

    if beta_val < 0:
        beta_val = 0

    

    return beta_val



def trade(info, exchange, coin, hedge_coin, acc_address, neu_address, coin_short):

    while True:
        time.sleep(40) # default 0.4
                        # 16 req/loop * 100 loop/min = 1600 weight/min; 16 req/loop * 60 loop/min = 960 w/m < 1200 weigh/min limit
        spot_balances = post_user_spot_tokens(acc_address, info)
        futures_positions = post_user_futures_summary(neu_address, info)
        futes_value = 0
        spot_sz = 0


        for position in futures_positions:
            if position["position"]['coin'] == hedge_coin:
                futes_value = float(position["position"]['positionValue'])
                futes_sz = float(position["position"]['szi'])
                break
 
        for balance in spot_balances:
            if balance["coin"] == coin_short:
                spot_sz = float(balance["total"])
                break

        leverage = beta(info, hedge_coin, coin)

        if leverage == 0:
            cprint("Beta is set to 0, skipping trade", 'white', 'on_red')
            continue
        futes_px, spot_px = allMids(info, hedge_coin, coin)
        spot_value = spot_sz * spot_px


        cprint(f"Spot Value: {spot_value}", 'light_green', 'on_blue')
        cprint(f"Futures Value: {futes_value}", 'light_green', 'on_blue')

        if futes_value  > 1.1 * leverage * spot_value:
            # Update Leverage
            update_leverage(exchange, hedge_coin, leverage, False)

            qty = round((futes_value - leverage * spot_value) / futes_px, 5)
            cprint(f"Qty: {qty}", 'light_green', 'on_blue')
            cprint(f"Px: {futes_px}", 'light_green', 'on_blue')
            #cancel all open orders and submit new order
            close_open_orders(exchange, info, neu_address, hedge_coin)
            futures_order( exchange, hedge_coin, True, qty, int(futes_px)-1, True, info)

    
        elif futes_value < 0.9 * leverage * spot_value:
            # Update Leverage
            update_leverage(exchange, hedge_coin, leverage, False)

            qty = round((leverage * spot_value - futes_value) / futes_px, 5)
            cprint(f"Qty: {qty}", 'light_green', 'on_blue')
            cprint(f"Px: {futes_px}", 'light_green', 'on_blue')
            #cancel all open orders and submit new order
            close_open_orders(exchange, info, neu_address, hedge_coin)
            futures_order( exchange, hedge_coin, False, qty, int(futes_px)+1, False, info)

