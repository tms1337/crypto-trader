from trading.daemon import Daemon
from trading.deciders.transaction.simple import AlwaysBuyTransactionDecider
from trading.deciders.volume.simple import FixedValueVolumeDecider
from trading.exchange.kraken.mocks import TradeProviderMock

import sys

from trading.exchange.kraken.trade import KrakenTradeProvider

daemon = None

try:
    base_currency = sys.argv[1]
    quote_currency = sys.argv[2]

    print("Starting daemon with base_currency: %s and quote_currency: %s" % (base_currency,
                                                                             quote_currency))

    always_buy_td = AlwaysBuyTransactionDecider(base_currency=base_currency,
                                                quote_currency=quote_currency)
    fixed_value_vd = FixedValueVolumeDecider(value=10)

    trader = TradeProviderMock(base_currency=base_currency,
                               quote_currency=quote_currency,
                               initial_balance=1000,
                               verbose=2)

    trader = KrakenTradeProvider(base_currency=base_currency,
                                 quote_currency=quote_currency,
                                 key_uri="/home/faruk/Desktop/key")

    daemon = Daemon(trader=trader,
                    transaction_decider=always_buy_td,
                    volume_decider=fixed_value_vd,
                    dt_seconds=10,
                    verbose=2)

except Exception as ex:
    print("Error while initializing daemon and its parts"
          "\n\tError message: %s" % str(ex))

daemon.run()

