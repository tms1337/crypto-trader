import time

import bot.exchange.poloniex.trade as poloniextrade

trader = poloniextrade.PoloniexTradeProvider(key_uri='/Users/farukmustafic/Desktop/alex_keys/poloniex')

print(trader.api.getMarginPosition('BTC_XRP'))

time.sleep(5)

coins = ['DASH', 'XRP']
while True:
    profit = {}
    for c in coins:
        profit[c] = float(trader.api.getMarginPosition('BTC_%s' % c.upper())['pl'])
        print('\tProfit for %s\t%f' % (c, profit[c]))

    total_profit = sum([v for _, v in profit.items()])

    if profit['DASH'] >= -0.5:
        trader.api.closeMarginPosition('BTC_DASH')

    if profit['XRP'] >= 0.05:
        trader.api.closeMarginPosition('BTC_XRP')

    print('Total profit %f' % total_profit)
    print()

    time.sleep(5)
