from abc import ABC, abstractmethod

from bot.exchange.base import TradeProvider
from bot.strategy.pipeline.informer import Informer
from bot.util.asserting import TypeChecker


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

