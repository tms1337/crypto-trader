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


trade = BittrexTradeProvider(key_uri="/home/faruk/Desktop/bittrex_key")
trade.set_currencies("ETH", "BTC")
id = trade.create_sell_offer(price=0.1, volume=0.1)
trade.cancel_offer(id)