from util.asserting import TypeChecker
from retrying import retry

from bot.exceptions.servererror import ServerError
from bot.exceptions.util import is_provider_error
from bot.exchange.base import StatsProvider, TradeProvider
from bot.strategy.pipeline.data.balancematrix import BalanceMatrix, BalanceCell
from bot.strategy.pipeline.data.statsmatrix import StatsMatrix, StatsCell
from util.logging import LoggableMixin

transactionexecutor_max_retry_attempts = None


class Informer(LoggableMixin):
    # ya' no say daddy me Snow me I go blame
    # A licky boom boom down

    def __init__(self,
                 stats_providers,
                 trade_providers,
                 currencies,
                 base_currency,
                 retry_attempts=3):

        TypeChecker.check_type(stats_providers, dict)
        for k in stats_providers:
            TypeChecker.check_type(stats_providers[k], StatsProvider)
        TypeChecker.check_type(currencies, list)

        TypeChecker.check_type(trade_providers, dict)
        for k in trade_providers:
            TypeChecker.check_type(trade_providers[k], TradeProvider)

        for currency in currencies:
            TypeChecker.check_type(currency, str)
        TypeChecker.check_type(base_currency, str)

        self.stats_providers = stats_providers
        self.trade_providers = trade_providers
        self.currencies = currencies
        self.base_currency = base_currency

        if not base_currency in currencies:
            currencies.append(base_currency)

        self.stats_matrix = StatsMatrix([e for e in stats_providers],
                                        currencies)
        self.balances_matrix = BalanceMatrix([e for e in trade_providers],
                                             currencies)

        global transactionexecutor_max_retry_attempts
        transactionexecutor_max_retry_attempts = retry_attempts

        LoggableMixin.__init__(self, Informer)

        self.set_stats_matrix()

    def set_stats_matrix(self):
        self.logger.debug("Getting stats matrix")
        for exchange in self.stats_providers:
            self.logger.debug("\tExchange %s" % exchange)
            for currency in self.currencies:
                self.logger.debug("\t\tCurrency %s" % currency)
                if currency == self.base_currency:
                    cell = self._generate_base_currency_stats_cell()
                else:
                    cell = self._generate_stats_cell(exchange, currency)
                self.stats_matrix.set(exchange, currency, cell)

    def get_stats_matrix(self):
        return self.stats_matrix

    def set_balances_matrix(self):
        self.logger.debug("Getting balance info")

        for exchange in self.trade_providers:
            self.logger.debug("\tExchange %s" % exchange)
            for currency in self.currencies:
                self.logger.debug("\t\tCurrency %s" % currency)
                cell = self._generate_balance_cell(exchange, currency)
                self.balances_matrix.set(exchange, currency, cell)

    def get_balances_matrix(self):
        return self.balances_matrix

    def set_all(self):
        self.set_stats_matrix()
        self.set_balances_matrix()

    def _generate_stats_cell(self, exchange, currency):
        assert exchange in self.stats_providers, \
            "Exchange %s not in a list" % exchange

        assert currency in self.currencies, \
            "Currency %s not in a list" % currency

        stats = self.stats_providers[exchange]

        stats.set_currencies(currency,
                             self.base_currency)

        cell = StatsCell()
        try:
            self._set_high(cell, stats)
        except (ConnectionError, ServerError):
            self.logger.error("Error in making request to server")
            cell.high = None
        except Exception as error:
            self.logger.error("Unexpected exception %s" % error)

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
           stop_max_attempt_number=transactionexecutor_max_retry_attempts)
    def _set_last(self, cell, stats):
        cell.last = stats.ticker_last()

    @retry(retry_on_exception=is_provider_error,
           stop_max_attempt_number=transactionexecutor_max_retry_attempts)
    def _set_low(self, cell, stats):
        cell.low = stats.ticker_low()

    @retry(retry_on_exception=is_provider_error,
           stop_max_attempt_number=transactionexecutor_max_retry_attempts)
    def _set_high(self, cell, stats):
        cell.high = stats.ticker_high()

    @retry(retry_on_exception=is_provider_error,
           stop_max_attempt_number=transactionexecutor_max_retry_attempts)
    def _generate_balance_cell(self, exchange, currency):
        assert exchange in self.trade_providers, \
            "Exchange %s not in list" % exchange

        assert currency in self.currencies, \
            "Currency %s not in list" % currency

        trader = self.trade_providers[exchange]

        cell = BalanceCell()
        cell.value = trader.total_balance(currency=currency)

        return cell

    def _generate_base_currency_stats_cell(self):
        cell = StatsCell()

        cell.high = 1.0
        cell.low = 1.0
        cell.last = 1.0

        return cell

