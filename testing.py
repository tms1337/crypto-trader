import krakenex

from trading.exchange.kraken.stats import KrakenStatsProvider
from trading.exchange.kraken.trade import KrakenTradeProvider

k = krakenex.API()
key_uri = "/home/faruk/Desktop/key"
k.load_key(key_uri)

base_currency = "XRP"
quote_currency = "XBT"
trader = KrakenTradeProvider(key_uri=key_uri,
                             base_currency=base_currency,
                             quote_currency=quote_currency)

stats = KrakenStatsProvider(base_currency=base_currency,
                            quote_currency=quote_currency)

last_price = stats.ticker_price()

print("Buying at price: %s" % last_price)

trader.create_sell_offer(volume=100, price=last_price)
