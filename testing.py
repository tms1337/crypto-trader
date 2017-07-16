import krakenex

from trading.exchange.bitfinex.base import PrivateBitfinexProvider
from trading.exchange.bitfinex.stats import BitfinexStatsProvider
from trading.exchange.bitfinex.trade import BitfinexTradeProvider
from trading.exchange.kraken.stats import KrakenStatsProvider
from trading.exchange.kraken.trade import KrakenTradeProvider
from trading.exchange.poloniex.stats import PoloniexStatsProvider
import poloniex

from trading.exchange.poloniex.trade import PoloniexTradeProvider

stats = BitfinexStatsProvider(base_currency="ETH",
                              quote_currency="BTC")

# print(stats.ticker_last())
# print(stats.ticker_high())
# print(stats.ticker_low())

trade = BitfinexTradeProvider(base_currency="ETH",
                              quote_currency="BTC",
                              key_uri="/home/faruk/Desktop/bitfinex_key")

print(trade.total_balance())