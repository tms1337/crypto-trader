import krakenex

from trading.exchange.bitfinex.base import PrivateBitfinexProvider
from trading.exchange.bitfinex.stats import BitfinexStatsProvider
from trading.exchange.bitfinex.trade import BitfinexTradeProvider
from trading.exchange.bittrex.stats import BittrexStatsProvider
from trading.exchange.bittrex.trade import BittrexTradeProvider
from trading.exchange.kraken.stats import KrakenStatsProvider
from trading.exchange.kraken.trade import KrakenTradeProvider
from trading.exchange.poloniex.stats import PoloniexStatsProvider
import poloniex

from trading.exchange.poloniex.trade import PoloniexTradeProvider


def bitfinex_test():
    stats = BitfinexStatsProvider(base_currency="ETH",
                                  quote_currency="BTC")

    print(stats.ticker_last())
    print(stats.ticker_high())
    print(stats.ticker_low())

    trade = BitfinexTradeProvider(base_currency="ETH",
                                  quote_currency="BTC",
                                  key_uri="/home/faruk/Desktop/bitfinex_key")

    print(trade.total_balance())


def bittrex_test():
    stats = BittrexStatsProvider(base_currency="ETH",
                                 quote_currency="BTC")

    print(stats.ticker_last())
    print(stats.ticker_high())
    print(stats.ticker_low())

    trade = BittrexTradeProvider(base_currency="ETH",
                                 quote_currency="BTC",
                                 key_uri="/home/faruk/Desktop/bittrex_key")

    print(trade.total_balance())

bittrex_test()
