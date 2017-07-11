from abc import ABC, abstractmethod

from trading.deciders.decision import TransactionType, Decision


class CurrencyMixin(ABC):
    def __init__(self,
                 base_currency=None,
                 quote_currency=None):
        self._check_arguments(base_currency,
                              quote_currency)

        self.base_currency = base_currency
        self.quote_currency = quote_currency

    def set_currencies(self, base_currency, quote_currency):
        self._check_arguments(base_currency, quote_currency)

        self.base_currency = base_currency
        self.quote_currency = quote_currency

    def form_pair(self):
        return "%s%s" % (self.base_currency,
                         self.quote_currency)

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
            if not isinstance(decision, Decision):
                if self.verbose >= 1:
                    print("Invalid decision object %s" % str(decision))
                failed_decisions.append(decision)
            try:
                if decision.transaction_type == TransactionType.BUY:
                    self.create_buy_offer(volume=decision.volume,
                                          price=decision.price)
                elif decision.transaction_type == TransactionType.SELL:
                    self.create_sell_offer(volume=decision.volume,
                                           price=decision.price)
            except Exception as ex:
                failed_decisions.append(decision)
                if self.verbose >= 1:
                    print("An error has occurred, %s" % str(ex))

        return failed_decisions

