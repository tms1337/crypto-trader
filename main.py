from trading.deciders.transaction.simple import AlwaysBuyTransactionDecider
from trading.deciders.volume.simple import FixedValueVolumeDecider
from trading.kraken.providers.mocks import TradeProviderMock
import time

always_buy_td = AlwaysBuyTransactionDecider(base_currency="XRP", quote_currency="XBT")

decisions = always_buy_td.decide()
print(str(decisions))

fixed_value_vd = FixedValueVolumeDecider(value=0.1)
decisions = fixed_value_vd.decide(decisions)

print(decisions)

trader = TradeProviderMock(base_currency="XRP", quote_currency="XBT", initial_balance=1000)
print(trader.total_balance())

for _ in range(100):
    trader.create_buy_offer(100)
    print(trader.total_balance())
    time.sleep(5)

