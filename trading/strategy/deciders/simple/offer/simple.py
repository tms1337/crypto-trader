from trading.strategy.deciders.simple.offer import TransactionDecider
from trading.strategy.decision import Decision, TransactionType


class SingleCurrencyPairOfferDecider(TransactionDecider):
    def __init__(self, base_currency, quote_currency, wrapper_container):
        self.base_currency = base_currency
        self.quote_currency = quote_currency

        self.currency_pair = "%s%s" % \
                             (self.base_currency, self.quote_currency)

        TransactionDecider.__init__(self, wrapper_container)

    def decide(self, prev_decisions):
        super().decide()

    def apply_last(self):
        super().apply_last()


class AlwaysBuyOfferDecider(SingleCurrencyPairOfferDecider):
    def decide(self):
        decision = Decision()
        decision.currency_pair = self.currency_pair
        decision.transaction_type = TransactionType.BUY
        decision.exchange = "kraken"

        return [decision]

    def apply_last(self):
        pass


class AlwaysSellOfferDecider(SingleCurrencyPairOfferDecider):
    def decide(self):
        decision = Decision()
        decision.currency_pair = self.currency_pair
        decision.transaction_type = TransactionType.SELL

        return [decision]

    def apply_last(self):
        pass