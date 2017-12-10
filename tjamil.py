import time

import bot.exchange.bitfinex.trade as bitfinex

trader = bitfinex.BitfinexTradeProvider(key_uri='/Users/farukmustafic/Desktop/our_keys/bitfinex')


class PositionType:
    IN = 0
    OUT = 1


position = PositionType.IN

thresh = 14000
step = 4000

while True:
    ticker = trader.api.ticker('btcusd')
    ask = float(ticker['ask'])
    bid = float(ticker['bid'])

    balances = trader.api.balances()
    balancesBtc = [b for b in balances if b['currency'] == 'btc']
    balanceBtc = float([b for b in balancesBtc if b['type'] == 'trading'][0]['available'])

    balancesUsd = [b for b in balances if b['currency'] == 'usd']
    balanceUsd = float([b for b in balancesUsd if b['type'] == 'trading'][0]['available'])

    print(ask, bid, balanceBtc, balanceUsd)

    if position == PositionType.IN and bid < thresh:
        print('Selling')

        print(trader.api.place_order(amount=str(balanceBtc),
                                     price=str(bid),
                                     ord_type="market",
                                     symbol='btcusd',
                                     side="sell"))
        position = PositionType.OUT

        time.sleep(2 * 60)
    elif position == PositionType.OUT and ask > thresh:
        print('Buying')

        print(trader.api.close_position(trader.api.active_positions()[0]['id']))

        time.sleep(2 * 60)

        position = PositionType.IN
    elif position == PositionType.IN and (ask + bid) / 2 > thresh + step:
        thresh += step
        print('Increasing threshold to %f' % thresh)

    time.sleep(60)
