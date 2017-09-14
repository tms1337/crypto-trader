import logging
import os
import sys

import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import scipy
import scipy.stats

from pymongo import MongoClient

# from bot.strategy.deciders.simple.offer.ema.reinforcement import ReinforcementEmaOfferDecider
from bot.strategy.deciders.simple.offer.ema.simple import SimpleEmaOfferDecider
from bot.strategy.deciders.simple.offer.percentbased import PercentBasedOfferDecider
from bot.strategy.decision import OfferType
from bot.strategy.pipeline.data.statsmatrix import StatsMatrix, StatsCell
from bot.strategy.pipeline.informer import Informer

import statsmodels.tsa.stattools as st

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
        cell.open = value[0]
        cell.high = value[1]
        cell.low = value[2]
        cell.last = value[3]
        cell.close = value[3]
        cell.volume = value[4]

        for e in self.stats_matrix.all_exchanges():
            for c in self.stats_matrix.all_currencies():
                self.stats_matrix.set(e, c, cell)

        return self.stats_matrix

def _get_values(table):
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
        values = df[['open', 'high', 'low', 'close', 'volume']].values

    np.save(cache_file_name, values)
    print('Got %d datapoints' % values.shape[0])

    return values

class EmaTests:
    def __init__(self, table, decider, parms, vol_percent, plot_steps=False):
        self.decider = decider
        self.table = table
        self.parms = parms
        self.plot_steps = plot_steps
        self.vol_percent = vol_percent

        values = _get_values(table)


        # closing_prices = [v[3] for v in values]
        # deltas = [ (closing_prices[i] - closing_prices[i-1]) / closing_prices[i - 1] for i in range(1, len(closing_prices)) ]
        #
        # deltas_hist = np.histogram(np.array(deltas), bins=20)
        #
        # hist = plt.hist(deltas, bins=40, range=(-0.1, 0.1))
        # print(hist)
        #
        # dist = scipy.stats.levy
        # param = dist.fit(hist[0])
        # pdf_fitted = dist.pdf(hist[1], *param[:-2], loc=param[-2], scale=param[-1]) * hist[1].shape[0]
        # plt.plot(pdf_fitted, label='levy')
        # plt.xlim(-1, 1)
        #
        # plt.show()
        #
        # input('stop')

        self.step_n = values.shape[0]
        self.informer = InformerHistoricDataMock(values, exchanges=['poloniex'], currencies=self.decider.currencies)

    def test_historical_data(self):
        decider = self.decider
        trading_currency = decider.trading_currency

        balances = {trading_currency: 40000}
        for c in decider.currencies:
            balances[c] = 0

        volumes = {c: 10 for c in decider.currencies}

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
                    # volume = self.vol_percent * 40000 / d.price

                    if d.transaction_type == OfferType.SELL:
                        volume = abs(balances[d.base_currency])
                        balances[trading_currency] -= d.price * volume
                        balances[d.base_currency] += volume
                        last_offer_type = OfferType.BUY
                        volumes[d.base_currency] = self.vol_percent * balances[trading_currency] / price
                        print('Buy', d.price, volume, d.price * volume, balances)
                    else:
                        balances[trading_currency] += d.price * volume
                        balances[d.base_currency] -= volume
                        last_offer_type = OfferType.SELL
                        print('Sell', d.price, volume, d.price * volume, balances)

            if last_offer_type == OfferType.BUY:
                color = 'r'
            else:
                color = 'b'

            balance_in_currencies = balances[trading_currency] + price * balances[decider.currencies[0]]
            if i % 100 == 0:
                trading_currency_balance_history.append((i, balance_in_currencies, color))
                print(balances)
            total_balance_history.append(balance_in_currencies)

            if self.plot_steps and i > 0 and i % (2 * 10 ** 3) == 0:
                print('Balances ', balances, ' price ', price)

                self.plot_history(price_history, total_balance_history, trading_currency_balance_history)

            if len(total_balance_history) >= 2:
                reward = 10000 * (total_balance_history[-2] - total_balance_history[-1]) / total_balance_history[-1]
                if reward < 0:
                    reward = - reward ** 2
                else:
                    reward = reward ** 2

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
    currency = 'BTC'
    percent = 0.33

    if False:
        btc_values = _get_values('poloniex_btc_usdt_5mins_3m_ohlcv')
        btc_values = np.array([math.log(v[3], 10) for v in btc_values])

        eth_values = _get_values('poloniex_eth_usdt_5mins_3m_ohlcv')
        eth_values = np.array([math.log(v[3], 10) for v in eth_values])

        min_len = min([ btc_values.shape[0], eth_values.shape[0] ])

        btc_values = btc_values[:min_len]
        eth_values = eth_values[:min_len]

        print(btc_values)
        print(eth_values)

        # btc_values = np.array( [ (btc_values[i] - btc_values[i-1]) / btc_values[i-1] for i in range(1, btc_values.shape[0])] )
        # eth_values = np.array( [ (eth_values[i] - eth_values[i-1]) / eth_values[i-1] for i in range(1, eth_values.shape[0])] )

        log_ratios = btc_values / eth_values

        print(st.adfuller(log_ratios, regresults=True))

        plt.plot(log_ratios)
        # plt.hist(btc_values / eth_values, range=(-2, 2), bins=500)

        plt.show()

        sys.exit(0)

    best_parms = None
    best_final_balance = None

    for first_period in [5]:
        for second_period in [10]:
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
                #                                        alpha=0.2,
                #                                        gamma=0.7)
                # decider = PercentBasedOfferDecider(currencies=[currency],
                #                                    trading_currency=trading_currency,
                #                                    buy_threshold=0.03,
                #                                    sell_threshold=0.01,
                #                                    security_loss_threshold=0.02)
                tests = EmaTests('poloniex_%s_%s_4h_3m_ohlcv' % (currency.lower(), trading_currency.lower()), decider,
                                 parms, percent, plot_steps=True)
                final_balance = tests.test_historical_data()

                if best_final_balance is None or final_balance > best_final_balance:
                    best_final_balance = final_balance
                    best_parms = parms

                print('Final balance for %s is %f' % (parms, final_balance))

    print('Best parms %s' % str(best_parms))
