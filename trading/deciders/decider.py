import logging
from abc import ABC

from trading.exchange.base import ExchangeWrapperContainer


class Decider:
    def __init__(self, wrapper_container, logger_name="app"):
        self._check_wrapper_container(wrapper_container)
        self.wrapper_container = wrapper_container
        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.Decider" % logger_name)

    def _check_wrapper_container(self, wrapper_container):
        if not isinstance(wrapper_container, ExchangeWrapperContainer):
            error_message = "Wrapper container must be an instance of \
                                ExchangeWrapperContainer"
            self.logger.error(error_message)
            raise ValueError(error_message)

    def _check_decision(self, decision):
        self.logger.debug("Checking decision %s", decision)

        exchange = decision.exchange
        wrapper = self.wrapper_container.wrappers[exchange]
        stats = wrapper.stats_provider

        balance = stats.total_balance()

        if not decision.quote_currency in balance or \
                        balance[decision.quote_currency] < decision.volume:

            error_message = "Balance not sufficient for transaction"

            self.logger.error(error_message)
            raise AssertionError(error_message)
