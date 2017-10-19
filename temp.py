import bot.exchange.bittrex.trade as bittrextrade
import bot.exchange.poloniex.trade as poloniextrade

trader = poloniextrade.PoloniexTradeProvider(key_uri='/Users/farukmustafic/Desktop/alex_keys/poloniex')
balance = trader.total_balance()

[print(b, balance[b]) for b in balance if balance[b] != 0]

trader.set_currencies('ETH', 'USD')
trader.create_sell_offer(volume=5, price=309.5)

# trader = bittrextrade.BittrexTradeProvider(key_uri='/home/faruk/Desktop/alex_keys/bittrex')
# print( trader.total_balance(currency='BTC') )

# trader.withdraw(currency='BTC',
#                 address='1JbcpCJtDmDKadjhMiuknFthrB7oY31xhU',
#                 quantity=4.9)

