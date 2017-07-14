from .base import TransactionDecider


class ExchangeDiffDecider(TransactionDecider):
    def __init__(self, currencies, wrapper_container):
        self.currencies = currencies
        TransactionDecider.__init__(self, wrapper_container)

    def decide(self):
        pass

    def apply_last(self):
        pass
