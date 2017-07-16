from trading.deciders.volume.base import VolumeDecider


class FixedIncomeVolumeDecider(VolumeDecider):
    def __init__(self, value, real_currency, wrapper_container):
        self.value = value
        self.real_currency = real_currency
        VolumeDecider.__init__(self, wrapper_container)

    def decide(self, partial_decisions):
        for decision in partial_decisions:
            if not isinstance(decision, tuple):
                raise ValueError("Only supporting tuple decisions")

            exchange = decision[0].exchange
            stats = self.wrapper_container.wrappers[exchange].stats_provider

            trading_currency = decision[0].quote_currency
            stats.set_currencies(trading_currency, self.real_currency)

            diff = decision[1].price - decision[0].price

            decision[0].volume = self.value / (stats.ticker_price() * diff)
            decision[1].volume = self.value / (stats.ticker_price() * diff)

        return partial_decisions
