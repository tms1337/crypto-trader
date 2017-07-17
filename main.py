from trading.daemon import Daemon
from trading.deciders.transaction.exchangediff import ExchangeDiffDecider, ExchangeDiffBackup
from trading.deciders.transaction.percentbased import PercentBasedTransactionDecider
from trading.deciders.transaction.simple import AlwaysBuyTransactionDecider
from trading.deciders.volume.fixedincome import FixedIncomeVolumeDecider
from trading.deciders.volume.simple import FixedValueVolumeDecider
from trading.exchange.base import ExchangeWrapper, ExchangeWrapperContainer
from trading.exchange.bitfinex.stats import BitfinexStatsProvider
from trading.exchange.bitfinex.trade import BitfinexTradeProvider
from trading.exchange.bittrex.stats import BittrexStatsProvider
from trading.exchange.bittrex.trade import BittrexTradeProvider
from trading.exchange.kraken.mocks import TradeProviderMock

import sys

from trading.exchange.kraken.stats import KrakenStatsProvider
from trading.exchange.kraken.trade import KrakenTradeProvider
from trading.exchange.poloniex.stats import PoloniexStatsProvider
from trading.exchange.poloniex.trade import PoloniexTradeProvider

import logging

# create logger with 'spam_application'
logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler('debug.log')
fh.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - '
                              '\n\t%(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

daemon = None

try:
    base_currency = "ETH"
    quote_currency = "BTC"
    dt = 60

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

    bittrex_stats = BittrexStatsProvider(base_currency=base_currency,
                                         quote_currency=quote_currency)

    bittrex_trader = BittrexTradeProvider(base_currency=base_currency,
                                          quote_currency=quote_currency,
                                          key_uri="/home/faruk/Desktop/bittrex_key")

    bittrex_wrapper = ExchangeWrapper(stats_provider=bittrex_stats,
                                      trade_provider=bittrex_trader)

    bitfinex_stats = BitfinexStatsProvider(base_currency=base_currency,
                                           quote_currency=quote_currency)

    bitfinex_trader = BitfinexTradeProvider(base_currency=base_currency,
                                            quote_currency=quote_currency,
                                            key_uri="/home/faruk/Desktop/bitfinex_key")

    bitfinex_wrapper = ExchangeWrapper(stats_provider=bitfinex_stats,
                                       trade_provider=bittrex_trader)

    wrappers = {
        "kraken": kraken_wrapper,
        # "poloniex": poloniex_wrapper,
        # "bittrex": bittrex_wrapper,
        # "bitfinex": bitfinex_wrapper
    }

    wrapper_container = ExchangeWrapperContainer(wrappers)

    trading_currencies = [base_currency, "XRP"]
    transaction_decider = ExchangeDiffDecider(trading_currency=quote_currency,
                                              currencies=trading_currencies,
                                              wrapper_container=wrapper_container,
                                              verbose=1)

    backup_transaction_decider = ExchangeDiffBackup(base_currency=quote_currency,
                                                    currencies=trading_currencies,
                                                    wrapper_container=wrapper_container,
                                                    verbose=1)

    volume_decider = FixedIncomeVolumeDecider(wrapper_container=wrapper_container,
                                              real_currency="USD",
                                              value=0.02,
                                              base_value_exchange="kraken")

    fixed_volume_decider = FixedValueVolumeDecider(wrapper_container=wrapper_container,
                                                   values={"ETH": 0.01, "XRP": 100, "LTC": 2, "ETC": 4})

    percent_based_transaction_decider = PercentBasedTransactionDecider(currencies=trading_currencies,
                                                                       trading_currency=quote_currency,
                                                                       wrapper_container=wrapper_container,
                                                                       sell_threshold=0.01,
                                                                       buy_threshold=0.01)

    daemon = Daemon(wrapper_container=wrapper_container,
                    dt_seconds=dt,
                    transaction_deciders=[transaction_decider],
                    volume_decider=fixed_volume_decider,
                    logger_name="app")

except Exception as ex:
    print("Error while initializing daemon and its parts"
          "\n\tError message: %s" % str(ex))

if daemon is not None:
    daemon.run()
