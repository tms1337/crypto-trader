import krakenex
import time

from trading.deciders.transaction.percentbased import PercentBasedTransactionDecider
from trading.exchange.base import ExchangeWrapper, ExchangeWrapperContainer
from trading.exchange.bitfinex.base import PrivateBitfinexProvider
from trading.exchange.bitfinex.stats import BitfinexStatsProvider
from trading.exchange.bitfinex.trade import BitfinexTradeProvider
from trading.exchange.bittrex.stats import BittrexStatsProvider
from trading.exchange.bittrex.trade import BittrexTradeProvider
from trading.exchange.kraken.mocks import StatsProviderMock, TradeProviderMock
from trading.exchange.kraken.stats import KrakenStatsProvider
from trading.exchange.kraken.trade import KrakenTradeProvider
from trading.exchange.poloniex.stats import PoloniexStatsProvider
import poloniex

from trading.exchange.poloniex.trade import PoloniexTradeProvider

stats = PoloniexStatsProvider()
stats.set_currencies("BTC", "USD")
trade = PoloniexTradeProvider(key_uri="/home/faruk/Desktop/poloniex_key")
trade.set_currencies("BTC", "USD")

id = trade.create_buy_offer(volume=0.01, price=stats.ticker_last())
trade.cancel_offer(id)

last_array = [1, 1, 0.89, 1.2, 1.2, 1.2, 1.2, 1, 0.79]
mock_stats = StatsProviderMock(high_array=[],
                               last_array=last_array,
                               low_array=[])
mock_trade = TradeProviderMock()

mock_wrapper = ExchangeWrapper(spending_factor=1,
                               stats_provider=mock_stats,
                               trade_provider=mock_trade)

wrapper_container = ExchangeWrapperContainer(wrappers={"kraken": mock_wrapper})

decider = PercentBasedTransactionDecider(buy_threshold=0.1,
                                         sell_threshold=0.1,
                                         security_loss_threshold=0.2,
                                         currencies=["ETH"],
                                         trading_currency="BTC",
                                         wrapper_container=wrapper_container)

for i in range(len(last_array) - 1):
    decisions = []
    decider.decide(decisions)
    for d in decisions:
        d.decider.apply_last()
    print(decisions)
