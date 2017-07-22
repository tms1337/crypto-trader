from retrying import retry

from trading.exceptions.servererror import ServerError
from trading.exceptions.util import is_provider_error
from trading.exchange.base import StatsProvider
from trading.strategy.pipeline.statsmatrix import StatsMatrix, StatsCell
from trading.util.asserting import TypeChecker
from trading.util.logging import LoggableMixin

max_retry_attempts = None


class Informer(LoggableMixin):
    # ya' no say daddy me Snow me I go blame
    # A licky boom boom down

    def __init__(self,
                 stats_providers,
                 currencies,
                 base_currency,
                 retry_attempts=3):

        TypeChecker.check_type(stats_providers, dict)
        for k in stats_providers:
            TypeChecker.check_type(stats_providers[k], StatsProvider)
        TypeChecker.check_type(currencies, list)

        for currency in currencies:
            TypeChecker.check_type(currency, str)

        TypeChecker.check_type(base_currency, str)

        self.stats_providers = stats_providers
        self.currencies = currencies
        self.base_currency = base_currency

        self.stats_matrix = StatsMatrix([e for e in stats_providers],
                                        currencies)

        global max_retry_attempts
        max_retry_attempts = retry_attempts

        LoggableMixin.__init__(self, Informer)

    def get_stats_matrix(self):
        self.logger.debug("Getting stats matrix")
        for exchange in self.stats_providers:
            self.logger.debug("Exchange %s" % exchange)
            for currency in self.currencies:
                self.logger.debug("\tCurrency %s" % currency)
                cell = self._generate_cell(exchange, currency)
                self.stats_matrix.set(exchange, currency, cell)

        return self.stats_matrix

    def _generate_cell(self, exchange, currency):
        try:
            stats = self.stats_providers[exchange]
        except KeyError:
            raise ValueError("Exchange %s not in a list" % exchange)

        stats.set_currencies(currency,
                             self.base_currency)

        cell = StatsCell()
        try:
            self._set_high(cell, stats)
        except (ConnectionError, ServerError):
            self.logger.error("Error in making request to server")
            cell.high = None
        except Exception as error:
            self.logger.error("Unexcpected exception %s" % error)

        try:
            self._set_low(cell, stats)
        except (ConnectionError, ServerError):
            cell.low = None
        except Exception:
            cell.high = None

        try:
            self._set_last(cell, stats)
        except (ConnectionError, ServerError):
            cell.last = None
        except Exception:
            cell.high = None

        return cell

    @retry(retry_on_exception=is_provider_error,
           stop_max_attempt_number=max_retry_attempts)
    def _set_last(self, cell, stats):
        cell.last = stats.ticker_last()
        pass

    @retry(retry_on_exception=is_provider_error,
           stop_max_attempt_number=max_retry_attempts)
    def _set_low(self, cell, stats):
        cell.low = stats.ticker_low()

    @retry(retry_on_exception=is_provider_error,
           stop_max_attempt_number=max_retry_attempts)
    def _set_high(self, cell, stats):
        cell.high = stats.ticker_high()
