import bot.exchange.bitfinex.trade as bitfinextrade
import time

trader = bitfinextrade.BitfinexTradeProvider(key_uri='/Users/farukmustafic/Desktop/our_keys/bitfinex')

while True:
    positions = [position for position in trader.api.active_positions() if position['symbol'] in ['ltcbtc']]
    profits = [float(p['pl']) for p in positions]

    print(sum(profits))

    if sum(profits) >= 0.05 or sum(profits) < -0.1:
        for p in positions:
            trader.api.close_position(p['id'])

    time.sleep(3)
