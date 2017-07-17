import logging
from abc import ABC, abstractmethod

from trading.deciders.decision import TransactionType, Decision


class CurrencyMixin(ABC):
    def __init__(self,
                 base_currency=None,
                 quote_currency=None,
                 logger_name="app"):

        self.set_currencies(base_currency, quote_currency)

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.CurrencyMixin" % logger_name)

    def set_currencies(self, base_currency, quote_currency):
        self._check_arguments(base_currency, quote_currency)

        if not (base_currency is None and quote_currency is None):
            self.check_currency(base_currency)
            self.check_currency(quote_currency)

            self.base_currency = self.map_currency(base_currency)
            self.quote_currency = self.map_currency(quote_currency)

    def form_pair(self):
        return "%s%s" % (self.base_currency,
                         self.quote_currency)

    @abstractmethod
    def map_currency(self, currency):
        pass

    @staticmethod
    def check_currency(currency):
        currency_list = ["BTC", "ETH", "XRP", "DASH"]

        return currency in currency_list

    def _check_arguments(self, base_currency, quote_currency):
        only_base_none = base_currency is None and quote_currency is not None
        only_quote_none = base_currency is not None and quote_currency is None

        if only_base_none or only_quote_none:
            error_message = "Either none or both currencies must be specified"

            self.logger.error(error_message)
            raise ValueError(error_message)


class StatsProvider(ABC):
    @abstractmethod
    def ohlc_history(self, interval=1, since=None):
        pass

    @abstractmethod
    def ticker_high(self):
        pass

    @abstractmethod
    def ticker_low(self):
        pass

    @abstractmethod
    def ticker_last(self):
        pass

    def last_ohlc(self, interval=1):
        history = self.ohlc_history(interval)

        last_ohlc = history[-1]

        return last_ohlc

    def last_open(self, interval=1):
        return float(self.last_ohlc(interval)[1])

    def last_high(self, interval=1):
        return float(self.last_ohlc(interval)[2])

    def last_low(self, interval=1):
        return float(self.last_ohlc(interval)[3])

    def last_close(self, interval=1):
        return float(self.last_ohlc(interval)[4])


class TradeProvider(ABC):
    def __init__(self, logger_name="app"):

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.TradeProvider" % logger_name)

    @abstractmethod
    def total_balance(self):
        pass

    @abstractmethod
    def create_buy_offer(self, volume, price=None):
        pass

    @abstractmethod
    def create_sell_offer(self, volume, price=None):
        pass

    def create_bulk_offers(self, decisions):
        failed_decisions = []

        for decision in decisions:
            try:
                self.execute_single_decision(decision)
            except Exception as ex:
                failed_decisions.append(decision)
                self.logger.error("An error has occurred, %s" % str(ex))

        return failed_decisions

    def execute_single_decision(self, decision):
        if not isinstance(decision, Decision):
            self.logger.error("Invalid decision object %s" % str(decision))
            raise ValueError("Invalid decision object")

        self.prepare_currencies(decision.base_currency,
                                decision.quote_currency)
        if decision.transaction_type == TransactionType.BUY:
            self.create_buy_offer(volume=decision.volume,
                                  price=decision.price)
        elif decision.transaction_type == TransactionType.SELL:
            self.create_sell_offer(volume=decision.volume,
                                   price=decision.price)

    def prepare_currencies(self, base_currency, quote_currency):
        pass


class ExchangeWrapper:
    def __init__(self,
                 trade_provider,
                 stats_provider,
                 logger_name="app"):

        self.trade_provider = trade_provider
        self.stats_provider = stats_provider

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.ExchangeWrapper" % logger_name)

    def _check_trader(self, trader):
        if not isinstance(trader, TradeProvider):
            error_message = "Trade provider must be instance of TradeProvider"

            self.logger.error(error_message)
            raise ValueError(error_message)

    def _check_stats_provider(self, stats_provider):
        if not isinstance(stats_provider, StatsProvider):
            error_message = "Stats provider must be instance of StatsProvider"

            self.logger.error(error_message)
            raise ValueError(error_message)


class ExchangeWrapperContainer:
    def __init__(self, wrappers=None, logger_name="app"):
        if wrappers is None:
            self.wrappers = {}
        else:
            self._check_wrappers(wrappers)
            self.wrappers = wrappers

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.ExchangeWrapperContainer" %
                                        logger_name)

    def add_wrapper(self, exchange, wrapper):
        self._check_wrapper(wrapper)
        self._check_exchange(exchange)
        self.wrappers[exchange] = wrapper

    def remove_wrapper(self, exchange):
        del self.wrappers[exchange]

    def create_bulk_offers(self, decisions):
        failed_decisions = []

        for i in range(len(decisions)):
            decision = decisions[i]
            if isinstance(decision, tuple):
                try:
                    for d in decision:
                        exchange = d.exchange
                        self.wrappers[exchange].trade_provider.execute_single_decision(d)
                except Exception as ex:
                    failed_decisions.append(decision)
            else:
                try:
                    exchange = decision.exchange
                    self.wrappers[exchange].trade_provider.execute_single_decision(decision)
                except Exception as ex:
                    failed_decisions.append(decision)

        return failed_decisions

    def _check_wrappers(self, wrappers):
        for exchange in wrappers:
            self._check_exchange(exchange)
            self._check_wrapper(wrappers[exchange])

    def print_balance(self):
        print_message = ""
        for exchange in self.wrappers:
            wrapper = self.wrappers[exchange]
            print_message += "Exchange: %s\n" % exchange
            total_balance = wrapper.trade_provider.total_balance()
            for currency in total_balance:
                if float(total_balance[currency]) != 0:
                    print_message += "\t\t%s: %s" % (currency, total_balance[currency]) + "\n"

        self.logger.debug(print_message)

    def _check_wrapper(self, wrapper):
        if not isinstance(wrapper, ExchangeWrapper):
            error_message = "Wrapper name must be an instance \
                             of ExchangeWrapper"
            self.logger.error(error_message)
            raise ValueError(error_message)

    def _check_exchange(self, exchange):
        if not isinstance(exchange, str):
            error_message = "Exchange name must be a string"

            self.logger.error(error_message)
            raise ValueError(error_message)
