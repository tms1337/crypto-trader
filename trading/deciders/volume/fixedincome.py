import logging

from trading.deciders.volume.base import VolumeDecider


class FixedIncomeVolumeDecider(VolumeDecider):
    def __init__(self,
                 value,
                 real_currency,
                 base_value_exchange,
                 wrapper_container,
                 logger_name="app"):

        self.value = value
        self.real_currency = real_currency
        self.base_value_exchange = base_value_exchange

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.FixedIncomeVolume" % logger_name)

        VolumeDecider.__init__(self, wrapper_container)

    def decide(self, partial_decisions):
        stats = self.wrapper_container.wrappers[self.base_value_exchange].stats_provider

        for decision in partial_decisions:
            if not isinstance(decision, tuple):
                raise ValueError("Only supporting tuple decisions")

            trading_currency = decision[0].quote_currency
            stats.set_currencies(trading_currency, self.real_currency)

            diff = decision[1].price - decision[0].price

            high_price_trading_currency = stats.ticker_high()
            decision[0].volume = self.value / (high_price_trading_currency * diff)
            decision[1].volume = self.value / (high_price_trading_currency * diff)

        return partial_decisions
