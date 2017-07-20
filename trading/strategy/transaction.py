from trading.strategy.decision import Decision
from trading.util.typechecker import TypeChecker


class Transaction:
    def __init__(self, decisions=None):
        if decisions is None:
            self.decisions = []
        else:
            TypeChecker.check_type(decisions, list)
            for d in decisions:
                TypeChecker.check_type(d, Decision)

            self.decisions = decisions

    def add_decision(self, decision):
        TypeChecker.check_type(decision, Decision)

        self.decisions.append(decision)
