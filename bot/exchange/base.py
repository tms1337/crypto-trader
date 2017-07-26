import logging
from abc import ABC, abstractmethod

import time

from bot.strategy.decision import OfferType, Decision
from bot.util.asserting import TypeChecker
from bot.util.logging import LoggableMixin


class CurrencyMixin(ABC, LoggableMixin):
    def __init__(self):
        LoggableMixin.__init__(self, CurrencyMixin)

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
    def currency_mapping(self):
        pass

    def map_currency(self, currency):
        return self.currency_mapping()[currency]

    @abstractmethod
    def currency_mapping_for_balance(self):
        pass

    def map_currency_balance(self, currency):
        return self.currency_mapping_for_balance()[currency]

    def inverse_map_currency(self, currency):
        currency_map = self.currency_mapping()
        inverse_currency_map = {currency_map[k]: k for k in currency_map}

        return inverse_currency_map[currency]

    @staticmethod
    def check_currency(currency):
        TypeChecker.check_type(currency, str)

        currency_list = ["BTC", "ETH", "XRP", "DASH",
                         "LTC", "USD", "EUR", "XRP"]

        return currency in currency_list

    def _check_arguments(self, base_currency, quote_currency):
        only_base_none = base_currency is None and quote_currency is not None
        only_quote_none = base_currency is not None and quote_currency is None

        if only_base_none or only_quote_none:
            error_message = "Either none or both currencies must be specified"

            self.logger.error(error_message)
            raise ValueError(error_message)


class Provider(ABC, LoggableMixin):
    def __init__(self, pause_dt=1):
        TypeChecker.check_one_of_types(pause_dt, [float, int])
        assert pause_dt > 0

        self.pause_dt = pause_dt

        LoggableMixin.__init__(self, Provider)

    @abstractmethod
    def _check_response(self, response):
        time.sleep(self.pause_dt)

    def _handle_error(self, error):
        self.logger.error("Encountered error %s " % error)
        self.logger.debug("Raising ConnectionError")
        raise ConnectionError()

    @abstractmethod
    def prepare_currencies(self, base_currency, quote_currency):
        pass


class StatsProvider(Provider):
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


class TradeProvider(Provider, LoggableMixin):
    def __init__(self):
        LoggableMixin.__init__(self, TradeProvider)

    @abstractmethod
    def total_balance(self, currency=None):
        pass

    @abstractmethod
    def create_buy_offer(self, volume, price=None):
        pass

    @abstractmethod
    def create_sell_offer(self, volume, price=None):
        pass

    @abstractmethod
    def cancel_offer(self, offer_id):
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

        id = None
        if decision.transaction_type == OfferType.BUY:
            id = self.create_buy_offer(volume=decision.volume,
                                       price=decision.price)
        elif decision.transaction_type == OfferType.SELL:
            id = self.create_sell_offer(volume=decision.volume,
                                        price=decision.price)

        if id is None:
            raise RuntimeError("Error while executing")
        else:
            decision.decider.apply_last()
            return id


class KeyLoaderMixin(ABC):
    def __init__(self, key_uri):
        self.key_uri = key_uri

        self._load_key()
        self._load_secret()

    def _load_key(self):
        content = self._get_key_file_content()
        self.key = content[0]

    def _load_secret(self):
        content = self._get_key_file_content()
        self.secret = content[1]

    def _get_key_file_content(self):
        with open(self.key_uri) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        return content
