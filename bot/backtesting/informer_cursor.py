from abc import abstractclassmethod, ABC, abstractmethod

from bot.strategy.pipeline.data.statsmatrix import StatsMatrix, StatsCell
from bot.strategy.pipeline.informer import Informer

# noinspection PyMissingConstructor
from util.asserting import TypeChecker

# noinspection PyMissingConstructor
from util.mongo import _connect_mongo


class InformerMock(Informer):
    def __init__(self,
                 stats_matrix):
        TypeChecker.check_type(stats_matrix, StatsMatrix)
        self.stats_matrix = stats_matrix

    def get_balances_matrix(self):
        raise NotImplementedError()

    def get_stats_matrix(self):
        return self.stats_matrix


class InformerCursor(ABC):
    @abstractclassmethod
    def next(self):
        pass


class InformerCursorMongoDb(InformerCursor):
    def __init__(self,
                 host,
                 port,
                 username,
                 password,
                 db_name,
                 currency_collections,
                 exchange='_BACKTEST_EXCHANGE'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.db_name = db_name
        self.exchange = exchange

        TypeChecker.check_type(currency_collections, dict)
        self.currency_collections = currency_collections

        self.db = _connect_mongo(host, port, username, password, db_name)
        self.cursors = {}
        for c in self.currency_collections:
            collection = self.currency_collections[c]
            self.cursors[c] = self.db[collection].find()

    def next(self):
        currencies = [c for c in self.currency_collections]

        stats_matrix = StatsMatrix(exchanges=self.exchange,
                                   currencies=currencies)



        for c in currencies:
            cell = StatsCell()

            cell.open, cell.high, cell.low, cell.close = self._get_ohlc(c)



            stats_matrix.set(self.exchange, c, cell)

        informer = InformerMock(stats_matrix)

        return informer

    def _get_ohlc(self, c):
        pass
