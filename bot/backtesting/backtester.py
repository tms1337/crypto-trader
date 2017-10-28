from bot.strategy.deciders.decider import Decider
from bot.strategy.pipeline.informer import Informer
from util.asserting import TypeChecker


class BackTester:
    def __init__(self, decider, informer_cursor, starting_money=1000):
        TypeChecker.check_type(decider, Decider)
        self.decider = decider

        TypeChecker.check_type(informer_cursor, Informer)
        self.informer_cursor = informer_cursor

        TypeChecker.check_type(starting_money, float)
        assert starting_money > 0
        self.money = starting_money

    def run_step(self):
        transactions, _ = self.decider.decide(self.informer_cursor)

        informer = self.informer_cursor.next()

        for t in transactions:
            for d in t.decisions:
                stats_matrix = informer.get_stats_matrix()

        informer = self.informer_cursor.next()

    def run_steps(self, step_n):
        TypeChecker.check_type(step_n, int)
        assert step_n > 0

        for _ in range(step_n):
            self.run_step()

    @property
    def state(self):
        return None
