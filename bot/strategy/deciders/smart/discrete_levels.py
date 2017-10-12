from bot.strategy.deciders.decider import Decider
from bot.strategy.decision import Decision, OfferType
from bot.strategy.transaction import Transaction
from util.asserting import TypeChecker

from collections import namedtuple

CurrencyInfo = namedtuple('CurrencyInfo', ['trends', 'referent_price', 'position', 'confidence'])


class DiscreteLevelsDecider(Decider):
    def __init__(self,
                 threshold=0.02,
                 trends_len=100,
                 *args,
                 **kwargs):
        Decider.__init__(self, *args, **kwargs)
        self.currency_infos = {e: {} for e in self.trade_providers}

        TypeChecker.check_type(threshold, float)
        assert 0 < threshold < 1

        TypeChecker.check_type(trends_len, int)
        assert trends_len > 0
        self.trends_len = trends_len

        self.threshold = threshold

    def decide(self, informer):
        Decider.decide(informer)

        stats = informer.get_stats_matrix()
        balances = informer.get_balances_matrix()

        for e in stats.all_exchanges():
            for c in stats.all_currencies():
                curr_price = stats.get(e, c).last
                if c not in self.currency_infos[e]:
                    self.currency_infos[e][c] = CurrencyInfo(trends=[],
                                                             referent_price=curr_price,
                                                             position=False,
                                                             confidence=0)

                referent_price = self.currency_infos[e][c].referent_price

                trend_val = None
                if curr_price - referent_price > self.threshold:
                    trend_val = 1
                elif curr_price - referent_price < -self.threshold:
                    trend_val = -1

                if trend_val is not None:
                    self.currency_infos[e][c].trends.append(trend_val)
                    self.currency_infos[e][c].trends = self.currency_infos[e][c].trends[-self.trends_len:]
                    self.currency_infos[e][c].referent_price = curr_price

        transaction = Transaction()


        for e in stats.all_exchanges():
            for c in stats.all_currencies():
                curr_price = stats.get(e, c).last
                referent_price = self.currency_infos[e][c].referent_price

                diff = curr_price - referent_price

                decision = Decision()
                decision.base_currency = informer.base_currency
                decision.quote_currency = c
                decision.exchange = e
                decision.price = curr_price
                decision.decider = self

                if self.currency_infos[e][c].position and self._should_sell(e, c):
                    decision.transaction_type = OfferType.SELL
                    decision.volume = balances.get(e, c).value

                    transaction.decisions.append(decision)
                elif not self.currency_infos[e][c].positions and self._should_buy(e, c):
                    decision.transaction_type = OfferType.BUY
                    decision.volume = balances.get(e, c).value

                    transaction.decisions.append(decision)

        return [transaction], {}

    def apply_last(self):
        super().apply_last()

    def _should_sell(self, e, c):
        return self.currency_infos[e][c].trends[-2:] == [-1, -1]

    def _should_buy(self, e, c):
        return self.currency_infos[e][c].trends[-2:] == [1, 1]