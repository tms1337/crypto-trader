import logging
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pymongo import MongoClient

# from bot.strategy.deciders.simple.offer.ema.reinforcement import ReinforcementEmaOfferDecider
from bot.strategy.deciders.simple.offer.ema.simple import SimpleEmaOfferDecider
from bot.strategy.decision import OfferType
from bot.strategy.pipeline.data.statsmatrix import StatsMatrix, StatsCell
from bot.strategy.pipeline.informer import Informer

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
    def __init__(self, table, decider, parms, vol_percent, plot_steps=False):
        self.decider = decider
        self.table = table
        self.parms = parms
        self.plot_steps = plot_steps
        self.vol_percent = vol_percent

        cache_file_name = 'cache/%s.npy' % table

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
        self.informer = InformerHistoricDataMock(values, exchanges=['poloniex'], currencies=self.decider.currencies)

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

        last_offer_type = None

        for i in range(self.step_n - 1):
            if i % 1000 == 0:
                print(i)

            transactions = decider.decide(self.informer)
            price = self.informer.get_stats_matrix(increment=False).get('poloniex', decider.currencies[0]).last

            price_history.append(price)

            for t in transactions:
                for d in t.decisions:
                    volume = volumes[d.base_currency]

                    if d.transaction_type == OfferType.BUY:
                        balances[trading_currency] -= d.price * volume
                        balances[d.base_currency] += volume * 0.9975
                        last_offer_type = OfferType.BUY
                    else:
                        balances[trading_currency] += d.price * volume * 0.9975
                        balances[d.base_currency] -= volume
                        volumes[d.base_currency] = self.vol_percent * balances[trading_currency] / price
                        last_offer_type = OfferType.SELL

            if last_offer_type == OfferType.BUY:
                color = 'r'
            else:
                color = 'b'

            balance_in_currencies = balances[trading_currency] + price * balances[decider.currencies[0]]
            if i % 8640 == 0:
                trading_currency_balance_history.append((i, balance_in_currencies, color))
            total_balance_history.append(balance_in_currencies)

            if self.plot_steps and i > 0 and i % (2 * 10 ** 3) == 0:
                print('Balances ', balances, ' price ', price)

                self.plot_history(price_history, total_balance_history, trading_currency_balance_history)

            if len(total_balance_history) >= 2:
                reward = 100 * (total_balance_history[-2] - total_balance_history[-1]) / total_balance_history[-1]
                if reward < 0:
                    reward *= 2

                # print('Reward %f' % reward)
            else:
                reward = 0

            decider.apply_last()
            # decider.apply_reward(reward)

        file_name = 'reports/%s_%s.png' % (self.table, self.parms)
        open(file_name, 'w+').close()

        self.plot_history(price_history, total_balance_history, trading_currency_balance_history)
        plt.savefig(file_name)

        return trading_currency_balance_history[-1][1]

    def plot_history(self, price_history, total_balance_history, trading_currency_balance_history):
        plt.clf()

        scaled_price_history = price_history / max(price_history)
        scaled_price_history *= max([b[1] for b in trading_currency_balance_history]) / 2
        plt.plot(scaled_price_history, color='g', alpha=0.7)

        for b in trading_currency_balance_history:
            plt.scatter([b[0]], [b[1]], color=b[2], marker='^')

        plt.plot(total_balance_history, color='b', alpha=0.4)
        plt.pause(0.001)


if __name__ == '__main__':
    trading_currency = 'USDT'
    currency = 'ETH'

    best_parms = None
    best_final_balance = None

    percent = 0.1

    for first_period in [100]:
        for second_period in [300]:
            if first_period < second_period:
                parms = (first_period, second_period, percent)
                print('Checking (%f, %f, %f)' % parms)

                decider = SimpleEmaOfferDecider(currencies=[currency],
                                                trading_currency=trading_currency,
                                                buy_threshold=1e-6,
                                                sell_threshold=1e-6,
                                                first_period=first_period,
                                                second_period=second_period)
                # decider = ReinforcementEmaOfferDecider(currencies=[currency],
                #                                        trading_currency=trading_currency,
                #                                        buy_threshold=1e-6,
                #                                        sell_threshold=1e-6,
                #                                        first_period=first_period,
                #                                        second_period=second_period,
                #                                        alpha=0.7,
                #                                        gamma=0.4)
                tests = EmaTests('poloniex_%s_%s_5mins_ohlcv' % (currency.lower(), trading_currency.lower()), decider,
                                 parms, percent, plot_steps=True)
                final_balance = tests.test_historical_data()

                if best_final_balance is None or final_balance > best_final_balance:
                    best_final_balance = final_balance
                    best_parms = parms

                print('Final balance for %s is %f' % (parms, final_balance))

    print('Best parms %s' % str(best_parms))
