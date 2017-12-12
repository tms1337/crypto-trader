import time

import bot.exchange.bitfinex.trade as bitfinex

trader = bitfinex.BitfinexTradeProvider(key_uri='/Users/farukmustafic/Desktop/our_keys/bitfinex')

class PositionType:
    IN = 0
    OUT = 1

position = PositionType.IN

upper = 18000
lower = 16000
step = (upper - lower) / 2

while True:
    try:
        ticker = trader.api.ticker('btcusd')
        ask = float(ticker['ask'])
        bid = float(ticker['bid'])

        balances = trader.api.balances()
        balancesBtc = [b for b in balances if b['currency'] == 'btc']
        balanceBtc = float([b for b in balancesBtc if b['type'] == 'exchange'][0]['available'])

        balancesUsd = [b for b in balances if b['currency'] == 'usd']
        balanceUsd = float([b for b in balancesUsd if b['type'] == 'exchange'][0]['available'])

        print('Ask: %f, Bid: %f, balanceBtc: %f, balanceUsd: %f, ul: (%f, %f)' % (ask, bid, balanceBtc, balanceUsd, upper, lower))

        if position == PositionType.IN and bid < lower:
            print('Selling at %f' % bid)

            print(trader.api.place_order(amount=str(balanceBtc),
                                         price=str(bid),
                                         ord_type="exchange market",
                                         symbol='btcusd',
                                         side="sell"))
            position = PositionType.OUT

            upper -= step
            lower -= step
        elif position == PositionType.OUT and ask > upper:
            print('Buying at %f' % ask)

            print(trader.api.place_order(amount=str(0.999*balanceUsd/ask),
                                         price=str(ask),
                                         ord_type="exchange market",
                                         symbol='btcusd',
                                         side="buy"))

            position = PositionType.IN

            upper += step
            lower += step
        elif (ask + bid) / 2 > upper:
            print('Increasing upper and lower to (%f, %f)' % (upper, lower))

            upper += step
            lower += step
    except Exception:
        continue

    time.sleep(60)