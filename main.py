from trading.daemon import Daemon
from trading.deciders.transaction.simple import AlwaysBuyTransactionDecider
from trading.deciders.volume.simple import FixedValueVolumeDecider
from trading.exchange.kraken.mocks import TradeProviderMock

daemon = None

try:
    always_buy_td = AlwaysBuyTransactionDecider(base_currency="XRP",
                                                quote_currency="XBT")
    fixed_value_vd = FixedValueVolumeDecider(value=100)

    trader = TradeProviderMock(base_currency="XRP",
                               quote_currency="XBT",
                               initial_balance=1000,
                               verbose=2)

    daemon = Daemon(trader=trader,
                    transaction_decider=always_buy_td,
                    volume_decider=fixed_value_vd,
                    dt_seconds=10,
                    verbose=2)

except Exception as ex:
    print("Error while initializing daemon and its parts"
          "\n\tError message: %s" % str(ex))

daemon.run()

