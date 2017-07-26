from bot.strategy.pipeline.data.infomatrix import InfoMatrix


class StatsCell:
    low = None
    high = None
    last = None
    open = None
    close = None
    price = None


class StatsMatrix(InfoMatrix):
    def __init__(self, exchanges, currencies):
        InfoMatrix.__init__(self, exchanges, currencies, StatsCell)