import bot.exchange.poloniex.trade as poloniextrade
import time

trader = poloniextrade.PoloniexTradeProvider(key_uri='/Users/farukmustafic/Desktop/my_keys/poloniex')

balances = trader.api.returnAvailableAccountBalances()
print(float(balances['exchange']['BTC']) + 0.125 + 0.46)