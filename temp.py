import time

import bot.exchange.bittrex.trade as bittrextrade
import bot.exchange.poloniex.trade as poloniextrade
import bot.exchange.poloniex.stats as poloniexstats

trader = poloniextrade.PoloniexTradeProvider(key_uri='/Users/farukmustafic/Desktop/alex_keys/poloniex')
balance = trader.total_balance()

prices = {}

stats = poloniexstats.PoloniexStatsProvider()

# trader.set_currencies('BTC', 'USD')
# trader.create_buy_offer(volume=1, price=6000)

unused = ['BTC', 'BCN', 'HUC', 'NOTE']

for c in balance:
    if balance[c] != 0 and c != 'USDT' and c not in unused:
        stats.set_currencies(c, 'BTC')
        prices[c] = stats.ticker_low()

prices['BTC'] = 1

totals = [(b, balance[b]) for b in balance if balance[b] != 0 and b not in unused]

print(totals)
print(sum([t[1] for t in totals]))

print(trader.api.getMarginPosition('BTC_ETH'))

while True:
    print(trader.api.getMarginPosition('BTC_ETH')['pl'])
    time.sleep(10)

# while True:
#     pos = trader.api.getMarginPosition('BTC_ETH')
#     print(pos['pl'])
#     time.sleep(10)
