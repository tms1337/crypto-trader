import time

import bot.exchange.poloniex.trade as bitfinex

trader = bitfinex.PoloniexTradeProvider(key_uri='/Users/farukmustafic/Desktop/alex_keys/poloniex')

pair = 'BTC_LTC'
print(trader.api.getMarginPosition(pair))
while True:
    pl = float(trader.api.getMarginPosition(pair)['pl'])

    print('PL: %f' % pl)
    if pl < -0.3:
        trader.api.closeMarginPosition(pair)
        break
    elif pl > 0.3:
        trader.api.closeMarginPosition(pair)
        break

    time.sleep(45)