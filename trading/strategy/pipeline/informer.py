from trading.exceptions.servererror import ServerError
from trading.exchange.base import StatsProvider
from trading.strategy.pipeline.statsmatrix import StatsMatrix, StatsCell
from trading.util.typechecker import TypeChecker


class Informer:
    # Informer, ya' no say daddy me Snow me I go blame
    # A licky boom boom down

    def __init__(self,
                 stats_providers,
                 currencies,
                 base_currency):

        self._check_argument_types(stats_providers,
                                   currencies,
                                   base_currency)

        self.stats_providers = stats_providers
        self.currencies = currencies
        self.base_currency = base_currency

        self.stats_matrix = StatsMatrix([e for e in stats_providers],
                                        currencies)

    def stats_matrix(self):
        for exchange in self.stats_providers:
            for currency in self.currencies:
                cell = self._generate_cell(exchange, currency)
                self.stats_matrix.set(exchange, currency, cell)

    def _check_argument_types(self, stats_providers, currencies, base_currency):
        TypeChecker.check_type(stats_providers, dict)
        for k in stats_providers:
            TypeChecker.check_type(stats_providers[k], StatsProvider)
        TypeChecker.check_type(currencies, list)

        for currency in currencies:
            TypeChecker.check_type(currency, str)

        TypeChecker.check_type(base_currency, str)

    def _generate_cell(self, exchange, currency):
        stats = self.stats_providers[exchange]
        stats.set_currency(currency,
                           self.base_currency)

        cell = StatsCell()
        try:
            cell.high = stats.ticker_high()
        except (ConnectionError, ServerError):
            cell.high = None
        except Exception:
            cell.high = None

        try:
            cell.low = stats.ticker_low()
        except (ConnectionError, ServerError):
            cell.low = None
        except Exception:
            cell.high = None

        try:
            cell.last = stats.ticker_last()
        except (ConnectionError, ServerError):
            cell.last = None
        except Exception:
            cell.high = None

        return cell
