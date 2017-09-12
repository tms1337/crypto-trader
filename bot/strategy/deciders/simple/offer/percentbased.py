from bot.strategy.deciders.simple.offer.pairedtrades import PairedTradesOfferDecider
from util.asserting import TypeChecker
from util.logging import LoggableMixin


class PercentBasedOfferDecider(PairedTradesOfferDecider, LoggableMixin):
    def __init__(self,
                 currencies,
                 trading_currency,
                 buy_threshold,
                 sell_threshold,
                 security_loss_threshold):
        TypeChecker.check_type(buy_threshold, float)
        assert 0 <= buy_threshold < 1 or buy_threshold == float("-inf"), \
            "Buy threshold must be in [0, 1) interval, value of %f given" % buy_threshold
        self.buy_threshold = buy_threshold

        TypeChecker.check_one_of_types(sell_threshold, [float, int])
        assert sell_threshold > 0, \
            "Sell threshold must be greater than 0, value of %f given" % buy_threshold
        self.sell_threshold = sell_threshold

        TypeChecker.check_type(security_loss_threshold, float)
        assert security_loss_threshold > 0, \
            "Security loss threshold must be greater than 0, value of %f given" % security_loss_threshold
        assert security_loss_threshold > buy_threshold, \
            "Security loss threshold must be greater than buy threshold, value of %f <= %f given" \
            % (security_loss_threshold, buy_threshold)
        self.security_loss_threshold = security_loss_threshold

        PairedTradesOfferDecider.__init__(self, currencies, trading_currency)
        LoggableMixin.__init__(self, PercentBasedOfferDecider)

        self.i = 0

    def should_buy(self, exchange, currency, low, high):
        self.i += 1

        last_applied_price = self.last_applied_decision_record.get(exchange, currency).price
        buy_margin = (last_applied_price - high) / last_applied_price

        self.logger.debug("\tBuy margin %f / %f" % (buy_margin, self.buy_threshold))

        return self.i > 50000 or buy_margin >= self.buy_threshold

    def should_sell(self, exchange, currency, low, high):
        last_applied_price = self.last_applied_decision_record.get(exchange, currency).price
        sell_margin = (low - last_applied_price) / last_applied_price

        self.logger.debug("\tSell margin %f / %f" % (sell_margin, self.sell_threshold))

        self.logger.debug("\t\tCurrent profit for last buy %f" % (sell_margin * last_applied_price))

        return (sell_margin >= self.sell_threshold or sell_margin <= -self.security_loss_threshold)


