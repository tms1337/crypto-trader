from abc import ABC, abstractmethod

from trading.exchange.base import TradeProvider
from trading.util.typechecker import TypeChecker


class Decider(ABC):
    def __init__(self, trade_provider):
        TypeChecker.check_type(trade_provider, TradeProvider)
        self.trade_provider = trade_provider

    @abstractmethod
    def decide(self, stats_matrix):
        pass

