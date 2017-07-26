from abc import ABC

from util.asserting import TypeChecker


class InfoMatrix(ABC):
    def __init__(self, exchanges, currencies, cell_type):
        TypeChecker.check_type(exchanges, list)
        for e in exchanges:
            TypeChecker.check_type(e, str)

        TypeChecker.check_type(currencies, list)
        for c in currencies:
            TypeChecker.check_type(c, str)

        TypeChecker.check_type(cell_type, type)

        self.matrix = {e: {c: None for c in currencies} for e in exchanges}

        self.exchanges = exchanges
        self.currencies = currencies

        self.cell_type = cell_type

    def get(self, exchange, currency):
        assert exchange in self.matrix, "Exchange %s not in matrix" % exchange
        assert currency in self.matrix[exchange], "Currency %s not in matrix" % currency

        return self.matrix[exchange][currency]

    def set(self, exchange, currency, cell):
        TypeChecker.check_type(exchange, str)
        TypeChecker.check_type(currency, str)
        TypeChecker.check_type(cell, self.cell_type)

        self.matrix[exchange][currency] = cell

    def all_exchanges(self):
        return self.exchanges

    def all_currencies(self):
        return self.currencies
