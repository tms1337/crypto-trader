import bot.exchange.bittrex.trade as bittrextrade
import bot.exchange.poloniex.trade as poloniextrade
import bot.exchange.poloniex.stats as poloniexstats

trader = poloniextrade.PoloniexTradeProvider(key_uri='/Users/farukmustafic/Desktop/alex_keys/poloniex')
balance = trader.total_balance()

prices = {}

stats = poloniexstats.PoloniexStatsProvider()

# trader.set_currencies('BTC', 'USD')
# trader.create_buy_offer(volume=1, price=6000)

for c in balance:
    if balance[c] != 0 and c != 'USDT' and c not in ['HUC', 'NOTE']:
        stats.set_currencies(c, 'USD')
        prices[c] = stats.ticker_low()

prices['USDT'] = 1

totals = [(b, balance[b]) for b in balance if balance[b] != 0 and b not in ['HUC', 'NOTE']]

print(totals)
print(sum([t[1] for t in totals]))

# trader.set_currencies('BTC', 'USD')
# trader.create_buy_offer(volume=1.5, price=5705)

# trader = bittrextrade.BittrexTradeProvider(key_uri='/home/faruk/Desktop/alex_keys/bittrex')
# print( trader.total_balance(currency='BTC') )

# trader.withdraw(currency='BTC',
#                 address='1JbcpCJtDmDKadjhMiuknFthrB7oY31xhU',
#                 quantity=4.9)

