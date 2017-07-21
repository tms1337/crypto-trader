from trading.util.asserting import TypeChecker


class StatsCell:
    low = None
    high = None
    last = None
    open = None
    close = None
    price = None


class StatsMatrix:
    def __init__(self, exchanges, currencies):
        TypeChecker.check_type(exchanges, list)
        for e in exchanges:
            TypeChecker.check_type(e, str)

        TypeChecker.check_type(currencies, list)
        for c in currencies:
            TypeChecker.check_type(c, str)

        self.matrix = {e: {c: None for c in currencies} for e in exchanges}

        self.exchanges = exchanges
        self.currencies = currencies

    def get(self, exchange, currency):
        return self.matrix[exchange][currency]

    def set(self, exchange, currency, cell):
        TypeChecker.check_type(exchange, str)
        TypeChecker.check_type(currency, str)
        TypeChecker.check_type(cell, StatsCell)

        self.matrix[exchange][currency] = cell

    def all_exchanges(self):
        return self.exchanges

    def all_currencies(self):
        return self.currencies
