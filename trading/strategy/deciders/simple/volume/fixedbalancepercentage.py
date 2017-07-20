import logging

from trading.strategy.deciders.simple.volume import VolumeDecider


class FixedBalancePercentageVolumeDecider(VolumeDecider):
    def __init__(self, percentage, wrapper_container, logger_name="app"):
        self.percentage = percentage
        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.FixedBalancePercentage" % logger_name)

        VolumeDecider.__init__(self,
                               wrapper_container,
                               logger_name)

    def decide(self, partial_decisions):
        for decision in partial_decisions:
            if not isinstance(decision, tuple) and decision.volume is None:
                self.decide_single(decision, partial_decisions)
            elif isinstance(decision, tuple) and decision[0].volume is None:
                for d in decision:
                    self.decide_single(d, partial_decisions)

        return partial_decisions

    def decide_single(self, d, partial_decisions):
        exchange = d.exchange
        trade = self.wrapper_container.wrappers[exchange].trade_provider

        try:
            currency = d.quote_currency
            total = trade.total_balance(currency=currency)

            d.volume = self.percentage * total * (1.0 / d.price)
        except Exception as ex:
            self.logger.error("Error %s" % ex)
            partial_decisions.remove(d)
