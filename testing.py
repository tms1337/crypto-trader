import krakenex

from trading.exchange.kraken.stats import KrakenStatsProvider
from trading.exchange.kraken.trade import KrakenTradeProvider
from trading.exchange.poloniex.stats import PoloniexStatsProvider
import poloniex

base_currency = "ETH"
quote_currency = "BTC"
kraken_key_uri = "/home/faruk/Desktop/key"

kraken_trader = KrakenTradeProvider(key_uri=kraken_key_uri,
                                    base_currency=base_currency,
                                    quote_currency=quote_currency)

kraken_stats = KrakenStatsProvider(base_currency=base_currency,
                                   quote_currency=quote_currency)

kraken_price = kraken_stats.ticker_price()

print("Kraken ticker price %f" % kraken_price)


polo_stats = PoloniexStatsProvider(base_currency="ETH",
                                   quote_currency="BTC")
price = polo_stats.ticker_price()
print("Poloniex ticker price: %f" % (price))
