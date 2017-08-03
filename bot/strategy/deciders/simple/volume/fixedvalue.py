from util.asserting import TypeChecker

from bot.strategy.deciders.simple.volume.base import VolumeDecider
from bot.strategy.decision import OfferType
from util.logging import LoggableMixin


class FixedValueVolumeDecider(VolumeDecider, LoggableMixin):
    def __init__(self,
                 values,
                 iceberg_n=5):
        TypeChecker.check_type(values, dict)
        for k in values:
            TypeChecker.check_type(k, str)
            TypeChecker.check_type(values[k], float)

        self.values = values

        TypeChecker.check_one_of_types(iceberg_n, [float, int])
        self.iceberg_n = iceberg_n

        LoggableMixin.__init__(self, FixedValueVolumeDecider)

    def decide(self, transactions, informer):
        balance_matrix = informer.get_balances_matrix()

        for transaction in transactions:
            for decision in transaction.decisions:
                exchange = decision.exchange

                base_currency = decision.base_currency
                quote_currency = decision.quote_currency
                quote_currency_balance = 0.8 * balance_matrix.get(exchange, quote_currency).value
                base_currency_balance = 0.8 * balance_matrix.get(exchange, base_currency).value
                quote_price = self.values[base_currency] * decision.price

                if decision.transaction_type == OfferType.BUY and \
                        quote_currency_balance < quote_price:
                    self.logger.warn("Balance of %f%s not sufficient, %f is required" %
                                     (quote_currency_balance, quote_currency, quote_price))
                    self.logger.debug("Clearing transaction %s" % transaction)
                    transaction.decisions = []
                elif decision.transaction_type == OfferType.SELL and \
                        base_currency_balance < self.values[base_currency]:
                    self.logger.warn("Balance of %f%s not sufficient, %f is required" %
                                     (base_currency_balance, base_currency, self.values[base_currency]))
                    self.logger.debug("Clearing transaction %s" % transaction)
                    transaction.decisions = []

                decision.volume = self.values[base_currency]

        return transactions

    def apply_last(self):
        pass
