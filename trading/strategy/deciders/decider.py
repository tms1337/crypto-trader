from abc import ABC, abstractmethod

from trading.exchange.base import TradeProvider
from trading.strategy.pipeline.informer import Informer
from trading.util.asserting import TypeChecker


class Decider(ABC):
    def __init__(self, trade_providers):
        TypeChecker.check_type(trade_providers, dict)
        for t in trade_providers:
            TypeChecker.check_type(trade_providers[t], TradeProvider)
        self.trade_providers = trade_providers

    @abstractmethod
    def decide(self, informer):
        TypeChecker.check_type(informer, Informer)

    @abstractmethod
    def apply_last(self):
        pass

