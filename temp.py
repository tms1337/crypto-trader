import time

import bot.exchange.bittrex.trade as bittrextrade
import bot.exchange.poloniex.trade as poloniextrade
import bot.exchange.poloniex.stats as poloniexstats

trader = bittrextrade.BittrexTradeProvider(key_uri='/Users/farukmustafic/Desktop/alex_keys/bittrex')
balances = trader.api.getbalances()
[print(b) for b in balances if b['Balance'] != 0]
exit(0)

# print(trader.api.returnTradableBalances())
#
while True:
    balances = trader.api.returnMarginAccountSummary()
    print(balances)
    time.sleep(2)
# [print(b, balances[b]) for b in balances if balances[b] != 0]
# print(balances['BTC_XRP'])
# [print(k, balance[k]) for k in balance if float(balance[k]) > 0]

# print(trader.api.marginSell('BTC_XMR', rate=0.0145, amount=250, lendingRate=0.04))

# print(trader.api.getMarginPosition('BTC_ETH'))

# print(trader.api.closeMarginPosition('BTC_LTC'))

# print(trader.api.returnOpenOrders('BTC_XMR'))

# print(trader.api.cancelOrder('212009036856'))

# trader.api.closeMarginPosition('BTC_ETH')
# trader.api.closeMarginPosition('BTC_XMR')
# trader.api.closeMarginPosition('BTC_XRP')
# trader.api.closeMarginPosition('BTC_DASH')

def get_position_pl(market):
    position = trader.api.getMarginPosition(market)
    print(market, position)
    return float(position['pl'])

while True:
    total = 0
    for market in ['BTC_XMR', 'BTC_ETH', 'BTC_DASH', 'BTC_XRP']:
        total += get_position_pl(market)
        time.sleep(2)

    print(total)

    time.sleep(3)

# trader.api.closeMarginPosition('BTC_ETH')

# while True:
#     pos = trader.api.getMarginPosition('BTC_ETH')
#     print(pos['pl'])
#     time.sleep(10)
