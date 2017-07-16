from trading.daemon import Daemon
from trading.deciders.transaction.exchangediff import ExchangeDiffDecider, ExchangeDiffBackup
from trading.deciders.transaction.simple import AlwaysBuyTransactionDecider
from trading.deciders.volume.fixedincome import FixedIncomeVolumeDecider
from trading.deciders.volume.simple import FixedValueVolumeDecider
from trading.exchange.base import ExchangeWrapper, ExchangeWrapperContainer
from trading.exchange.kraken.mocks import TradeProviderMock

import sys

from trading.exchange.kraken.stats import KrakenStatsProvider
from trading.exchange.kraken.trade import KrakenTradeProvider
from trading.exchange.poloniex.stats import PoloniexStatsProvider
from trading.exchange.poloniex.trade import PoloniexTradeProvider

daemon = None

try:
    base_currency = "ETH"
    quote_currency = "BTC"
    dt = 30

    print("Starting daemon with base_currency: %s and quote_currency: %s" % (base_currency,
                                                                             quote_currency))

    kraken_trader = KrakenTradeProvider(base_currency=base_currency,
                                        quote_currency=quote_currency,
                                        key_uri="/home/faruk/Desktop/kraken_key")

    kraken_stats = KrakenStatsProvider(base_currency=base_currency,
                                       quote_currency=quote_currency)

    kraken_wrapper = ExchangeWrapper(stats_provider=kraken_stats,
                                     trade_provider=kraken_trader)

    poloniex_stats = PoloniexStatsProvider(base_currency=base_currency,
                                           quote_currency=quote_currency)

    poloniex_trader = PoloniexTradeProvider(base_currency=base_currency,
                                            quote_currency=quote_currency,
                                            key_uri="/home/faruk/Desktop/poloniex_key")

    poloniex_wrapper = ExchangeWrapper(stats_provider=poloniex_stats,
                                       trade_provider=poloniex_trader)

    wrappers = {"kraken": kraken_wrapper,
                "poloniex": poloniex_wrapper}

    wrapper_container = ExchangeWrapperContainer(wrappers)

    trading_currencies = [base_currency]
    transaction_decider = ExchangeDiffDecider(base_currency=quote_currency,
                                              currencies=trading_currencies,
                                              wrapper_container=wrapper_container,
                                              verbose=1)
    backup_transaction_decider = ExchangeDiffBackup(base_currency=quote_currency,
                                                    currencies=trading_currencies,
                                                    wrapper_container=wrapper_container,
                                                    verbose=1)

    volume_decider = FixedIncomeVolumeDecider(wrapper_container=wrapper_container,
                                              real_currency="USD",
                                              value=0.4)

    daemon = Daemon(wrapper_container=wrapper_container,
                    dt_seconds=dt,
                    transaction_deciders=[transaction_decider, backup_transaction_decider],
                    volume_decider=volume_decider,
                    verbose=1)

except Exception as ex:
    print("Error while initializing daemon and its parts"
          "\n\tError message: %s" % str(ex))

if daemon is not None:
    daemon.run()
