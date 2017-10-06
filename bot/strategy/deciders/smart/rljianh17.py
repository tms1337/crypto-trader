from tensorforce.agents import Agent

from bot.strategy.deciders.decider import Decider
from bot.strategy.decision import Decision, OfferType
from bot.strategy.transaction import Transaction
from util.asserting import TypeChecker

import numpy as np

from util.logging import LoggableMixin


class RLJianh17Decide(Decider, LoggableMixin):
    def __init__(self, agent, *args, **kwargs):
        TypeChecker.check_type(agent, Agent)
        self.agent = agent

        Decider.__init__(self, *args, **kwargs)
        LoggableMixin.__init__(self, RLJianh17Decide)

    def decide(self, informer):
        super().decide(informer)

        historic_data = informer.get_historic_data()

        self._normalize_historic_data(historic_data)

        action = self.agent.act(historic_data, deterministic=True)

        action = sorted(action.items(), key=lambda x: x[0])
        action = action[1:]
        action = [a[1] for a in action]

        print(action)

        action = np.exp(action)
        action /= sum(action)

        e = 'poloniex' # :( hc
        currencies = informer.get_stats_matrix().all_currencies()

        total = 0
        for c in currencies:
            balance = informer.get_balances_matrix().get(e, c).value
            price = informer.get_stats_matrix().get(e, c)
            price = 0.5 * (price.low + price.high)

            total += balance * price
            self.logger.debug('currency %s, balance %f, price %f', c, balance, price)

        total *= 0.98 # because of floating point errors

        self.logger.debug('Total %f', total)

        transaction = Transaction()
        for i in range(len(currencies[:-1])):
            c = currencies[i]

            balance = informer.get_balances_matrix().get(e, c).value

            price = informer.get_stats_matrix().get(e, c)
            price = 0.5 * (price.low + price.high)

            curr_p = price * balance / total
            next_p = action[i]

            self.logger.debug('Curr p: %s, next p: %f' % (curr_p, next_p))

            delta = abs(curr_p - next_p) * total

            decision = Decision()
            decision.exchange = e
            decision.base_currency = c
            decision.quote_currency = currencies[-1]
            decision.price = price
            decision.volume = delta / price

            if next_p < curr_p:
                decision.transaction_type = OfferType.SELL
            else:
                decision.transaction_type = OfferType.BUY

            self.logger.debug('Curr: %s, decision %s' % (c, decision))
            transaction.add_decision(decision)

        self.logger.debug(transaction)

        return [transaction], {}

    def _normalize_historic_data(self, historic_data):
        for i in range(historic_data.shape[0]):
            historic_data[i] /= historic_data[i, -1, 0]

    def apply_last(self):
        super().apply_last()
