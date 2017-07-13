from abc import ABC

from trading.exchange.base import ExchangeWrapperContainer


class Decider:
    def __init__(self, wrapper_container):
        self._check_wrapper_container(wrapper_container)
        self.wrapper_container = wrapper_container

    @staticmethod
    def _check_wrapper_container(wrapper_container):
        if not isinstance(wrapper_container, ExchangeWrapperContainer):
            raise ValueError("Wrapper container must be an instance of \
                                ExchangeWrapperContainer")
