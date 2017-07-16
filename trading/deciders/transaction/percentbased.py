from trading.deciders.transaction.base import TransactionDecider


class PercentBasedTransactionDecider(TransactionDecider):
    def __init__(self, threshold, wrapper_container):
        self.threshold = threshold
        self.wrapper_container = wrapper_container

        TransactionDecider.__init__(self, wrapper_container)

    def decide(self, prev_decisions):
        pass

    def apply_last(self):
        pass