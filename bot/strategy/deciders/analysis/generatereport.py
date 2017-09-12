import os
import unittest

from pymongo import MongoClient

from bot.strategy.deciders.simple.offer.ema import EmaDecider
from bot.strategy.deciders.simple.offer.percentbased import PercentBasedOfferDecider
from bot.strategy.decision import OfferType
from bot.strategy.pipeline import informer
from bot.strategy.pipeline.data.statsmatrix import StatsMatrix, StatsCell
from bot.strategy.pipeline.informer import Informer

import pandas as pd
import numpy as np
import logging
import sys

import matplotlib.pyplot as plt

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
# create console handler with a higher log level
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter(fmt="[%(asctime)s / %(name)s / %(levelname)s / %(funcName)s]\t"
                                  "%(message)s", datefmt="%Y-%m-%d,%H:%M")
ch.setFormatter(formatter)


# add the handlers to the logger
# logger.addHandler(ch)

def _connect_mongo(host, port, username, password, db):
    """ A util for making a connection to mongo """

    if username and password:
        mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
        conn = MongoClient(mongo_uri)
    else:
        conn = MongoClient(host, port)

    return conn[db]


def read_mongo(db, collection, query=None, host='localhost', port=27017, username=None, password=None, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Connect to MongoDB
    if query is None:
        query = {}
    db = _connect_mongo(host=host, port=port, username=username, password=password, db=db)

    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)

    # Expand the cursor and construct the DataFrame
    df = pd.DataFrame(list(cursor))

    # Delete the _id
    if no_id and '_id' in df:
        del df['_id']

    return df


class InformerHistoricDataMock(Informer):
    def __init__(self, values, exchanges, currencies):
        self.stats_matrix = StatsMatrix(exchanges=exchanges, currencies=currencies)
        self.values = values
        self.i = 0

    def get_stats_matrix(self, increment=True):
        value = self.values[self.i]
        if increment:
            self.i += 1

        cell = StatsCell()
        cell.high = value[1]
        cell.low = value[2]
        cell.last = value[3]

        for e in self.stats_matrix.all_exchanges():
            for c in self.stats_matrix.all_currencies():
                self.stats_matrix.set(e, c, cell)

        return self.stats_matrix


class EmaTests:
    def __init__(self, table, decider, parms):
        self.decider = decider
        self.table = table
        self.parms = parms

        cache_file_name = '%s.npy' % table

        if os.path.exists(cache_file_name):
            print('Getting data from cached file')

            values = np.load(cache_file_name)
        else:
            print('Getting data from DB')

            mongo_host = '35.177.25.74'
            mongo_port = 27017

            df = read_mongo('historicalData',
                            table,
                            host=mongo_host,
                            port=mongo_port)
            values = df[['open', 'high', 'low', 'close']].values

        np.save(cache_file_name, values)
        print('Got %d datapoints' % values.shape[0])

        self.step_n = values.shape[0]
        self.informer = InformerHistoricDataMock(values, exchanges=['poloniex'], currencies=['BTC'])

    def test_historical_data(self):
        decider = self.decider
        trading_currency = decider.trading_currency

        balances = {trading_currency: 1000}
        for c in decider.currencies:
            balances[c] = 0

        volumes = {c: 1 for c in decider.currencies}

        trading_currency_balance_history = []
        total_balance_history = []
        price_history = []
        plt.ion()

        for i in range(self.step_n - 1):
            transactions = decider.decide(self.informer)
            price = self.informer.get_stats_matrix(increment=False).get('poloniex', 'BTC').last

            price_history.append(price)

            for t in transactions:
                for d in t.decisions:
                    if d.transaction_type == OfferType.BUY:
                        balances[trading_currency] -= d.price * volumes[d.base_currency]
                        balances[d.base_currency] += volumes[d.base_currency]
                    else:
                        balances[trading_currency] += d.price * volumes[d.base_currency]
                        balances[d.base_currency] -= volumes[d.base_currency]

            trading_currency_balance_history.append(balances[trading_currency])
            total_balance_history.append(balances[trading_currency] + price * balances['BTC'])
            if total_balance_history[-1] <= 0:
                break

            decider.apply_last()

        plt.clf()
        plt.plot(trading_currency_balance_history)
        plt.plot(price_history)

        file_name = '%s_%s.png' % (self.table, self.parms)
        open(file_name, 'w+').close()
        plt.savefig(file_name)

        return total_balance_history[-1]


if __name__ == '__main__':
    trading_currency = 'USDT'

    best_parms = None
    best_final_balance = None

    for first_period in reversed([50]):
        for second_period in [150]:
            if first_period < second_period:
                parms = (first_period, second_period)
                print('Checking (%f, %f)' % parms)

                decider = EmaDecider(currencies=['BTC'],
                                     trading_currency=trading_currency,
                                     buy_threshold=1e-6,
                                     sell_threshold=1e-6,
                                     first_period=first_period,
                                     second_period=second_period)
                tests = EmaTests('poloniex_btc_usdt_5mins_ohlcv', decider, parms)
                final_balance = tests.test_historical_data()

                print('Final balance for %s is %f' % (parms, final_balance))

                if best_final_balance is None or final_balance > best_final_balance:
                    best_final_balance = final_balance
                    best_parms = parms


    print('Best parms %s' % best_parms)