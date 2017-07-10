from trading.deciders.decision import Decision, TransactionType
from trading.deciders.transaction.base import TransactionDecider


class AlwaysBuyTransactionDecider(TransactionDecider):
    def __init__(self, currency_pair):
        self.currency_pair = currency_pair

    def decide(self):
        decision = Decision()
        decision.currency_pair = self.currency_pair
        decision.transaction_type = TransactionType.BUY

        return [ decision ]

    def apply_last(self):
        pass


class AlwaysSellTransactionDecider(TransactionDecider):
    def __init__(self, currency_pair):
        self.currency_pair = currency_pair

    def decide(self):
        decision = Decision()
        decision.currency_pair = self.currency_pair
        decision.transaction_type = TransactionType.SELL

        return [ decision ]

    def apply_last(self):
        pass
