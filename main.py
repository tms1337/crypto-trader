from trading.daemon import Daemon
from trading.deciders.decision import Decision, TransactionType
from trading.deciders.transaction.exchangediff import ExchangeDiffDecider, ExchangeDiffBackup
from trading.deciders.transaction.percentbased import PercentBasedTransactionDecider
from trading.deciders.transaction.simple import AlwaysBuyTransactionDecider
from trading.deciders.volume.fixedbalancepercentage import FixedBalancePercentageVolumeDecider
from trading.deciders.volume.fixedincome import FixedIncomeVolumeDecider
from trading.deciders.volume.simple import FixedValueVolumeDecider
from trading.exchange.base import ExchangeWrapper, ExchangeWrapperContainer
from trading.exchange.bitfinex.stats import BitfinexStatsProvider
from trading.exchange.bitfinex.trade import BitfinexTradeProvider
from trading.exchange.bittrex.stats import BittrexStatsProvider
from trading.exchange.bittrex.trade import BittrexTradeProvider
from trading.exchange.kraken.mocks import TradeProviderMock, StatsProviderMock

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
                              '%(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

daemon = None

try:
    quote_currency = "BTC"
    dt = 30
    key_directory = sys.argv[1]

    print("Here")

    kraken_stats = KrakenStatsProvider()
    kraken_trader = KrakenTradeProvider(key_uri=("%s/kraken_key" % key_directory))

    kraken_wrapper = ExchangeWrapper(stats_provider=kraken_stats,
                                     trade_provider=kraken_trader,
                                     spending_factor=1)

    poloniex_stats = PoloniexStatsProvider()
    poloniex_trader = PoloniexTradeProvider(key_uri=("%s/poloniex_key" % key_directory))
    poloniex_wrapper = ExchangeWrapper(stats_provider=poloniex_stats,
                                       trade_provider=poloniex_trader,
                                       spending_factor=0.2)

    bittrex_stats = BittrexStatsProvider()
    bittrex_trader = BittrexTradeProvider(key_uri=("%s/bittrex_key" % key_directory))
    bittrex_wrapper = ExchangeWrapper(stats_provider=bittrex_stats,
                                      trade_provider=bittrex_trader,
                                      spending_factor=0.2)

    bitfinex_stats = BitfinexStatsProvider()
    bitfinex_trader = BitfinexTradeProvider(key_uri=("%s/bitfinex_key" % key_directory))
    bitfinex_wrapper = ExchangeWrapper(stats_provider=bitfinex_stats,
                                       trade_provider=bittrex_trader,
                                       spending_factor=0.2)

    bitfinex_stats.set_currencies("ETH", "BTC")
    bitfinex_trader.set_currencies("ETH", "BTC")
    bitfinex_trader.create_sell_offer(volume=0.1, price=bitfinex_stats.ticker_last())

    kraken_mock_stats = StatsProviderMock([9, 10, 8], [9, 10, 8], [1, 10.5, 1])
    kraken_mock_trade = TradeProviderMock()

    # kraken_wrapper = ExchangeWrapper(stats_provider=kraken_mock_stats,
    #                                  trade_provider=kraken_mock_trade)


    wrappers = {
        "kraken": kraken_wrapper,
        # "poloniex": poloniex_wrapper,
        # "bittrex": bittrex_wrapper,
        # "bitfinex": bitfinex_wrapper
    }

    wrapper_container = ExchangeWrapperContainer(wrappers)

    # decision = Decision()
    # decision.exchange = "kraken"
    # decision.base_currency = "ETH"
    # decision.quote_currency = "BTC"
    # kraken_stats.set_currencies("ETH", "BTC")
    # decision.price = kraken_stats.ticker_last()
    # decision.volume = 0.1
    # decision.transaction_type = TransactionType.BUY
    #
    # wrapper_container.create_bulk_offers([decision])

    trading_currencies = ["ETH", "ICN"]
    transaction_decider = ExchangeDiffDecider(trading_currency=quote_currency,
                                              currencies=trading_currencies,
                                              wrapper_container=wrapper_container)

    backup_transaction_decider = ExchangeDiffBackup(trading_currency=quote_currency,
                                                    currencies=trading_currencies,
                                                    wrapper_container=wrapper_container)

    volume_decider = FixedIncomeVolumeDecider(wrapper_container=wrapper_container,
                                              real_currency="USD",
                                              value=0.10,
                                              base_value_exchange="poloniex")

    fixed_volume_decider = FixedValueVolumeDecider(wrapper_container=wrapper_container,
                                                   values={"ETH": 1, "ICN": 100,"XRP": 200, "LTC": 2, "ETC": 4})

    fixed_percentage_volume_decider = FixedBalancePercentageVolumeDecider(wrapper_container=wrapper_container,
                                                                          percentage=0.2)

    percent_based_transaction_decider = PercentBasedTransactionDecider(currencies=trading_currencies,
                                                                       trading_currency=quote_currency,
                                                                       wrapper_container=wrapper_container,
                                                                       sell_threshold=0.1,
                                                                       buy_threshold=0.02,
                                                                       security_loss_threshold=0.2)

    daemon = Daemon(wrapper_container=wrapper_container,
                    dt_seconds=dt,
                    transaction_deciders=[percent_based_transaction_decider],
                    volume_deciders=[fixed_volume_decider],
                    logger_name="app")

except Exception as ex:
    print("Error while initializing daemon and its parts"
          "\n\tError message: %s" % str(ex))

if daemon is not None:
    daemon.run()
