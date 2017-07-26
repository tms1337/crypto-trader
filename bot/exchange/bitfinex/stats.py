import FinexAPI.FinexAPI as finex

from bot.exchange.base import StatsProvider
from bot.exchange.bitfinex.base import BitfinexProvider
from util.logging import LoggableMixin


class BitfinexStatsProvider(BitfinexProvider,
                            StatsProvider,
                            LoggableMixin):
    def __init__(self,
                 api=finex,
                 pause_dt=1):

        LoggableMixin.__init__(self, BitfinexStatsProvider)
        BitfinexProvider.__init__(self, api, pause_dt)

    def ticker_last(self):
        try:
            ticker_response = self.api.ticker(symbol=self.form_pair())
        except Exception as error:
            self._handle_error(error)

        self._check_response(ticker_response)

        return float(ticker_response["last_price"])

    def ticker_low(self):
        try:
            ticker_response = self.api.ticker(symbol=self.form_pair())
        except Exception as error:
            self.logger.error("Encountered error %s " % error)
            self.logger.debug("Raising ConnectionError")
            raise ConnectionError()

        self._check_response(ticker_response)

        return float(ticker_response["low"])

    def ticker_high(self):
        try:
            ticker_response = self.api.ticker(symbol=self.form_pair())
        except Exception as error:
            self.logger.error("Encountered error %s " % error)
            self.logger.debug("Raising ConnectionError")
            raise ConnectionError()

        self._check_response(ticker_response)

        return float(ticker_response["high"])

    def ohlc_history(self, interval=1, since=None):
        raise NotImplementedError()


