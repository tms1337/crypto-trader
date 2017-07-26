from bot.strategy.decision import Decision
from bot.util.asserting import TypeChecker


class Transaction:
    def __init__(self, decisions=None):
        if decisions is None:
            decisions = []

        TypeChecker.check_type(decisions, list)
        for d in decisions:
            TypeChecker.check_type(d, Decision)

        self.decisions = decisions

    def add_decision(self, decision):
        TypeChecker.check_type(decision, Decision)

        self.decisions.append(decision)

    def __str__(self):
        transaction_str = "{ Decisions: "
        for d in self.decisions:
            transaction_str += str(d) + ", "

        transaction_str += "}"

        return transaction_str

    def __repr__(self):
        return self.__str__()
