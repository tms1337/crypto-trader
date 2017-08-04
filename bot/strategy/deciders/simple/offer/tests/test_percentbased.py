import pickle
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


class PercentBasedDeciderTests(unittest.TestCase):
    def setUp(self):
        self.currencies = ["ETH"]
        self.exchanges = ["bittrex"]

    def test_single_buy_zero_threshold(self):
        self.decider = PercentBasedOfferDecider(buy_threshold=0,
                                                sell_threshold=0.1,
                                                currencies=self.currencies,
                                                trading_currency="BTC",
                                                security_loss_threshold=0.2)

        self.informer = InformerMock([1, 1, 1, 1.11, 1.11],
                                     self.exchanges,
                                     self.currencies)

        self._assert_buy()
        self._assert_none()
        self._assert_none()
        self._assert_sell()
        self._assert_buy()

    def test_single_buy_nonzero_threshold(self):
        self.decider = PercentBasedOfferDecider(buy_threshold=0.1,
                                                sell_threshold=0.1,
                                                currencies=self.currencies,
                                                trading_currency="BTC",
                                                security_loss_threshold=0.2)

        self.informer = InformerMock([1, 1, 0.89, 0.91, 0.99, 0.99, 0.99, 0.89],
                                     self.exchanges,
                                     self.currencies)

        self._assert_none()
        self._assert_none()
        self._assert_buy()
        self._assert_none()
        self._assert_sell()
        self._assert_none()
        self._assert_none()
        self._assert_buy()

    def test_single_cycle_nonzero_buy(self):
        self.decider = PercentBasedOfferDecider(buy_threshold=0.1,
                                                sell_threshold=0.1,
                                                currencies=self.currencies,
                                                trading_currency="BTC",
                                                security_loss_threshold=0.2)

        self.informer = InformerMock([1, 1, 0.89, 0.9, 0.91,
                                      0.92, 0.93, 0.98, 1],
                                     self.exchanges,
                                     self.currencies)

        self._assert_none()
        self._assert_none()
        self._assert_buy()
        self._assert_none()
        self._assert_none()

        self._assert_none()
        self._assert_none()
        self._assert_sell()
        self._assert_none()

    def test_security_loss(self):
        self.decider = PercentBasedOfferDecider(buy_threshold=0.1,
                                                sell_threshold=0.1,
                                                currencies=self.currencies,
                                                trading_currency="BTC",
                                                security_loss_threshold=0.2)

        self.informer = InformerMock([1, 1, 1, 0.79, 0.57],
                                     self.exchanges,
                                     self.currencies)

        self._assert_none()
        self._assert_none()
        self._assert_none()
        self._assert_buy()
        self._assert_sell()

    def test_multiple_cycles_zero_buy_threshold(self):
        self.decider = PercentBasedOfferDecider(buy_threshold=0,
                                                sell_threshold=0.01,
                                                currencies=self.currencies,
                                                trading_currency="BTC",
                                                security_loss_threshold=0.05)

        self.informer = InformerMock([1, 1, 1, 1, 1.01, 1.01, 1.015, 1.03, 1.03, 0.96],
                                     self.exchanges,
                                     self.currencies)

        self._assert_buy()
        self._assert_none()
        self._assert_none()
        self._assert_none()
        self._assert_sell()
        self._assert_buy()
        self._assert_none()
        self._assert_sell()
        self._assert_buy()
        self._assert_sell()

    def _assert_sell(self):
        self._assert_type(OfferType.SELL)

    def _assert_buy(self):
        self._assert_type(OfferType.BUY)

    def _assert_type(self, type):
        transactions = self.decider.decide(self.informer)
        self.assertEqual(len(transactions), 1)
        decision = transactions[0].decisions[0]
        self.assertEqual(decision.transaction_type, type)
        self.decider.apply_last()

    def _assert_none(self):
        transactions = self.decider.decide(self.informer)
        self.assertEqual(len(transactions), 1)
        decisions = transactions[0].decisions
        self.assertEqual(len(decisions), 0)
        self.decider.apply_last()


if __name__ == '__main__':
    unittest.main()
