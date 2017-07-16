import krakenex

from trading.exchange.bitfinex.base import PrivateBitfinexProvider
from trading.exchange.bitfinex.stats import BitfinexStatsProvider
from trading.exchange.kraken.stats import KrakenStatsProvider
from trading.exchange.kraken.trade import KrakenTradeProvider
from trading.exchange.poloniex.stats import PoloniexStatsProvider
import poloniex

from trading.exchange.poloniex.trade import PoloniexTradeProvider

stats = BitfinexStatsProvider(base_currency="ETH",
                              quote_currency="BTC")

stats.ticker_last()
