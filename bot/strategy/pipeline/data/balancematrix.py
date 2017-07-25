from trading.strategy.pipeline.data.infomatrix import InfoMatrix


class BalanceCell:
    value = None

class BalanceMatrix(InfoMatrix):
    def __init__(self, exchanges, currencies):
        InfoMatrix.__init__(self, exchanges, currencies, BalanceCell)