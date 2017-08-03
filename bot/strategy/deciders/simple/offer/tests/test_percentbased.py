import unittest

from bot.strategy.deciders.simple.offer.percentbased import PercentBasedOfferDecider
from bot.strategy.decision import OfferType
from bot.strategy.pipeline.data.statsmatrix import StatsMatrix, StatsCell
from bot.strategy.pipeline.informer import Informer


class InformerMock(Informer):
    def __init__(self, values, exchanges, currencies):
        self.stats_matrix = StatsMatrix(exchanges=exchanges, currencies=currencies)
        self.values = values
        self.i = 0

    def get_stats_matrix(self):
        value = self.values[self.i]
        self.i += 1

        cell = StatsCell()
        cell.high = value
        cell.low = value
        cell.last = value

        for e in self.stats_matrix.all_exchanges():
            for c in self.stats_matrix.all_currencies():
                self.stats_matrix.set(e, c, cell)

        return self.stats_matrix


class MyTestCase(unittest.TestCase):
    def test_ctor(self):
        pass

    def test_single_buy_zero_threshold(self):
        currencies = ["ETH"]
        exchanges = ["bittrex"]
        decider = PercentBasedOfferDecider(buy_threshold=0,
                                           sell_threshold=0.1,
                                           currencies=currencies,
                                           trading_currency="BTC",
                                           security_loss_threshold=0.2)

        informer = InformerMock([1, 1, 1], exchanges, currencies)
        transactions = decider.decide(informer)

        self.assertEqual(len(transactions), 1)
        decision = transactions[0].decisions[0]

        self.assertEqual(decision.transaction_type, OfferType.BUY)

    def test_single_buy_nonzero_threshold(self):
        currencies = ["ETH"]
        exchanges = ["bittrex"]
        decider = PercentBasedOfferDecider(buy_threshold=0.1,
                                           sell_threshold=0.1,
                                           currencies=currencies,
                                           trading_currency="BTC",
                                           security_loss_threshold=0.2)

        informer = InformerMock([1, 1, 0.89], exchanges, currencies)

        transactions = decider.decide(informer)
        self.assertEqual(len(transactions), 1)
        decisions = transactions[0].decisions
        self.assertEqual(len(decisions), 0)

        transactions = decider.decide(informer)
        self.assertEqual(len(transactions), 1)
        decisions = transactions[0].decisions
        self.assertEqual(len(decisions), 0)

        transactions = decider.decide(informer)
        self.assertEqual(len(transactions), 1)
        decisions = transactions[0].decisions
        self.assertEqual(len(decisions), 1)
        decision = decisions[0]
        self.assertEqual(decision.transaction_type, OfferType.BUY)

    def test_single_cycle(self):
        currencies = ["ETH"]
        exchanges = ["bittrex"]
        decider = PercentBasedOfferDecider(buy_threshold=0.1,
                                           sell_threshold=0.1,
                                           currencies=currencies,
                                           trading_currency="BTC",
                                           security_loss_threshold=0.2)

        informer = InformerMock([1, 1, 0.89, 0.9, 0.97, 1], exchanges, currencies)

        transactions = decider.decide(informer)
        self.assertEqual(len(transactions), 1)
        decisions = transactions[0].decisions
        self.assertEqual(len(decisions), 0)
        decider.apply_last()

        transactions = decider.decide(informer)
        self.assertEqual(len(transactions), 1)
        decisions = transactions[0].decisions
        self.assertEqual(len(decisions), 0)
        decider.apply_last()

        transactions = decider.decide(informer)
        self.assertEqual(len(transactions), 1)
        decisions = transactions[0].decisions
        self.assertEqual(len(decisions), 1)
        decision = decisions[0]
        self.assertEqual(decision.transaction_type, OfferType.BUY)
        decider.apply_last()

        transactions = decider.decide(informer)
        self.assertEqual(len(transactions), 1)
        decisions = transactions[0].decisions
        self.assertEqual(len(decisions), 0)
        decider.apply_last()

        transactions = decider.decide(informer)
        self.assertEqual(len(transactions), 1)
        decisions = transactions[0].decisions
        self.assertEqual(len(decisions), 0)
        decider.apply_last()

        transactions = decider.decide(informer)
        self.assertEqual(len(transactions), 1)
        decisions = transactions[0].decisions
        self.assertEqual(len(decisions), 1)
        decision = decisions[0]
        self.assertEqual(decision.transaction_type, OfferType.SELL)



if __name__ == '__main__':
    unittest.main()
