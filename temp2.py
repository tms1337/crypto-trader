import bot.exchange.poloniex.trade as poloniextrade
import time

trader = poloniextrade.PoloniexTradeProvider(key_uri='/Users/farukmustafic/Desktop/my_keys/poloniex')


class PositionType:
    IN = 0
    OUT = 1


position = PositionType.IN

upper = 18000
lower = 16000
step = (upper - lower) / 2

while True:
    try:
        ticker = trader.api.returnTicker()['USDT_BTC']
        ask = float(ticker['lowestAsk'])
        bid = float(ticker['highestBid'])

        balances = trader.api.returnAvailableAccountBalances('exchange')['exchange']
        balanceBtc = float(balances['BTC'])
        balanceUsd = float(balances['USDT'])

        print('Ask: %f, Bid: %f, balanceBtc: %f, balanceUsd: %f, ul: (%f, %f)' % (
        ask, bid, balanceBtc, balanceUsd, upper, lower))

        if position == PositionType.IN and bid < lower:
            print('Selling at %f' % bid)

            print(trader.api.sell('USDT_BTC', rate=bid, amount=balanceBtc))
            position = PositionType.OUT

            upper -= step
            lower -= step
        elif position == PositionType.OUT and ask > upper:
            print('Buying at %f' % ask)

            print(trader.api.buy('USDT_BTC', rate=ask, amount=0.999 * balanceUsd / ask))

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
