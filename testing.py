from trading.exchange.base import ExchangeWrapper, ExchangeWrapperContainer
from trading.exchange.kraken.mocks import StatsProviderMock, TradeProviderMock
from trading.strategy.deciders.simple.offer import PercentBasedTransactionDecider

last_array = [1, 1, 1, 1.05, 0.95, 1.1, 1.1, 1.1, 0.95, 0.95, 0.95, 2, 1.95, 1.95]
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

for i in range(len(last_array)):
    decisions = []
    decider.decide(decisions)
    for d in decisions:
        d.decider.apply_last()
    print(decisions)
