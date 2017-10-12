from bot.strategy.deciders.decider import Decider
from bot.strategy.decision import Decision, OfferType
from bot.strategy.transaction import Transaction
from util.asserting import TypeChecker

from collections import namedtuple


class CurrencyInfo:
    def __init__(self,
                 trends,
                 referent_price,
                 position,
                 confidence,
                 last_price):
        self.trends = trends
        self.referent_price = referent_price
        self.position = position
        self.confidence = confidence
        self.last_price = last_price


class DiscreteLevelsDecider(Decider):
    def __init__(self,
                 threshold=0.02,
                 trends_len=10,
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

        self.first = True

    def decide(self, informer):
        Decider.decide(self, informer)

        stats = informer.get_stats_matrix()
        balances = informer.get_balances_matrix()

        currencies = informer.get_stats_matrix().all_currencies()
        base_currency = currencies[-1]

        for e in stats.all_exchanges():
            for c in stats.all_currencies()[:-1]:
                curr_price = stats.get(e, c).last
                if c not in self.currency_infos[e]:
                    self.currency_infos[e][c] = CurrencyInfo(trends=[],
                                                             referent_price=curr_price,
                                                             position=False,
                                                             confidence=1,
                                                             last_price=None)

                referent_price = self.currency_infos[e][c].referent_price

                trend_val = None
                if curr_price - referent_price > self.threshold:
                    trend_val = 1
                elif curr_price - referent_price < -self.threshold:
                    trend_val = -1

                if trend_val is not None:
                    self.currency_infos[e][c].trends.append(trend_val)
                    if len(self.currency_infos[e][c].trends) >= self.trends_len:
                        self.currency_infos[e][c].trends = self.currency_infos[e][c].trends[-self.trends_len:]
                    self.currency_infos[e][c].referent_price = curr_price

        transaction = Transaction()

        for e in stats.all_exchanges():
            for c in stats.all_currencies()[:-1]:
                curr_price = stats.get(e, c).last
                referent_price = self.currency_infos[e][c].referent_price

                diff = curr_price - referent_price

                decision = Decision()
                decision.base_currency = informer.base_currency
                decision.quote_currency = c
                decision.exchange = e
                decision.price = curr_price
                decision.decider = self

                c_balance = balances.get(e, c).value
                c__security = self.currency_infos[e][c].confidence
                currency_n = len(self.currency_infos)

                if self.currency_infos[e][c].position and self._should_sell(e, c):
                    decision.transaction_type = OfferType.SELL
                    decision.volume = c_balance

                    transaction.decisions.append(decision)

                    self.currency_infos[e][c].position = False

                    if curr_price > self.currency_infos[e][c].last_price:
                        self.currency_infos[e][c].confidence *= 1.2
                    else:
                        self.currency_infos[e][c].confidence /= 1.2

                elif not self.currency_infos[e][c].position and self._should_buy(e, c):
                    decision.transaction_type = OfferType.BUY
                    decision.volume = balances.get(e, base_currency).value * c__security / (2 * currency_n)

                    transaction.decisions.append(decision)

                    self.currency_infos[e][c].position = True
                    self.currency_infos[e][c].last_price = curr_price

        self.first = False

        return [transaction], {}

    def apply_last(self):
        super().apply_last()

    def _should_sell(self, e, c):
        if self.first:
            return False

        trends = self.currency_infos[e][c].trends
        return self.currency_infos[e][c].position and \
               len(trends) >= 2 and trends[-2:] == [-1, -1]

    def _should_buy(self, e, c):
        if self.first:
            return True

        trends = self.currency_infos[e][c].trends
        return not self.currency_infos[e][c].position and \
               len([_ for _ in trends if _ == 1]) > len(trends) / 2
