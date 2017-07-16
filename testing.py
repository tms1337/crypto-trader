import krakenex

from trading.exchange.kraken.stats import KrakenStatsProvider
from trading.exchange.kraken.trade import KrakenTradeProvider
from trading.exchange.poloniex.stats import PoloniexStatsProvider
import poloniex

from trading.exchange.poloniex.trade import PoloniexTradeProvider

base_currency = "DASH"
quote_currency = "BTC"
# kraken_key_uri = "/home/faruk/Desktop/kraken_key"
#
# kraken_trader = KrakenTradeProvider(key_uri=kraken_key_uri,
#                                     base_currency=base_currency,
#                                     quote_currency=quote_currency)
#
# kraken_stats = KrakenStatsProvider(base_currency=base_currency,
#                                    quote_currency=quote_currency)
#
# kraken_price = kraken_stats.ticker_price()
#
# print("Kraken ticker price %f" % kraken_price)

polo_stats = PoloniexStatsProvider(base_currency="ETH",
                                   quote_currency="BTC")
price = polo_stats.ticker_high()
print("Poloniex ticker price: %f" % (price))

polo_trader = PoloniexTradeProvider(base_currency=base_currency,
                                    quote_currency=quote_currency,
                                    key_uri="/home/faruk/Desktop/poloniex_key")

print(polo_trader.total_balance())
polo_trader.create_buy_offer(price, 0.1)
