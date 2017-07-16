from abc import ABC, abstractmethod

from trading.deciders.decision import TransactionType, Decision


class CurrencyMixin(ABC):
    def __init__(self,
                 base_currency=None,
                 quote_currency=None):
        self._check_arguments(base_currency,
                              quote_currency)

        self.base_currency = self.map_currency(base_currency)
        self.quote_currency = self.map_currency(quote_currency)

    def set_currencies(self, base_currency, quote_currency):
        self._check_arguments(base_currency, quote_currency)
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

    @staticmethod
    def _check_arguments(base_currency, quote_currency):
        only_base_none = base_currency is None and quote_currency is not None
        only_quote_none = base_currency is not None and quote_currency is None

        if only_base_none or only_quote_none:
            raise ValueError("Either none or both currencies must be specified")


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
    def __init__(self, verbose=1):
        self.verbose = verbose

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
                if self.verbose >= 1:
                    print("An error has occurred, %s" % str(ex))

        return failed_decisions

    def execute_single_decision(self, decision):
        if not isinstance(decision, Decision):
            if self.verbose >= 1:
                print("Invalid decision object %s" % str(decision))
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
                 stats_provider):

        self.trade_provider = trade_provider
        self.stats_provider = stats_provider

    @staticmethod
    def _check_trader(trader):
        if not isinstance(trader, TradeProvider):
            raise ValueError("Trade provider must be instance of TradeProvider")

    @staticmethod
    def _check_stats_provider(stats_provider):
        if not isinstance(stats_provider, StatsProvider):
            raise ValueError("Stats provider must be instance of StatsProvider")


class ExchangeWrapperContainer:
    def __init__(self, wrappers=None):
        if wrappers is None:
            self.wrappers = {}
        else:
            self._check_wrappers(wrappers)
            self.wrappers = wrappers

    def add_wrapper(self, exchange, wrapper):
        self._check_wrapper(wrapper)
        self._check_exchange(exchange)
        self.wrappers[exchange] = wrapper

    def remove_wrapper(self, exchange):
        del self.wrappers[exchange]

    def create_bulk_offers(self, decisions):
        failed_decisions = []

        for decision in decisions:
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
        for exchange in self.wrappers:
            wrapper = self.wrappers[exchange]
            print("Exchange: %s" % exchange)
            total_balance = wrapper.trade_provider.total_balance()
            for currency in total_balance:
                if float(total_balance[currency]) != 0:
                    print("\t\t%s: %s" % (currency, total_balance[currency]))
            print()

    @staticmethod
    def _check_wrapper(wrapper):
        if not isinstance(wrapper, ExchangeWrapper):
            raise ValueError("Wrapper name must be an instance \
                             of ExchangeWrapper")

    @staticmethod
    def _check_exchange(exchange):
        if not isinstance(exchange, str):
            raise ValueError("Exchange name must be a string")
