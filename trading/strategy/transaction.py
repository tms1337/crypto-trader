from trading.strategy.decision import Decision


class Transaction:
    def __init__(self, decisions=None):
        self._check_decisions(decisions)

        if decisions is None:
            self.decisions = []
        else:
            self.decisions = decisions

    def _check_decisions(self, decisions):
        if decisions is not None:
            for d in decisions:
                self._check_decision(d)

    def _check_decision(self, d):
        if not isinstance(d, Decision):
            raise TypeError("Parameter not of Decision type")
