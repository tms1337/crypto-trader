import logging
import sys

import matplotlib.pyplot as plt

from bot.strategy.deciders.analysis.datahelper import _get_values
from bot.strategy.deciders.simple.offer.ema.simple import SimpleEmaOfferDecider
from bot.strategy.deciders.simple.offer.percentbased import PercentBasedOfferDecider
from bot.strategy.decision import OfferType
from bot.strategy.pipeline.data.statsmatrix import StatsMatrix, StatsCell
from bot.strategy.pipeline.informer import Informer


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

class MongoDataMock(Informer):
    def __init__(self,exchanges=['poloniex'], currencies=['BTC']):
        self.stats_matrix = StatsMatrix(exchanges=exchanges, currencies=currencies)

        from pymongo import MongoClient

        mongo_host = '35.177.25.74'
        mongo_port = 27017

        client = MongoClient(mongo_host, mongo_port)
        self.db = client['historicalData']
        self.collection = self.db['bitfinex_btc_tick']

        self.cursor = self.collection.find()
        # self.cursor.skip(6000 * 10**3)

        self.last_price = 0

    def get_stats_matrix(self, increment=True):
        if increment:
            success = False

            while not success:
                try:
                    data = self.cursor.next()

                    price = float(data['price'])
                    volume = float(data['volume'])

                    cell = StatsCell()
                    cell.open = price
                    cell.high = price
                    cell.low = price
                    cell.last = price
                    cell.close = price
                    cell.volume = volume
                    cell.type = str(data['type']).replace("'", '').replace(' ', '')

                    success = True
                except Exception as ex:
                    success = False

            for e in self.stats_matrix.all_exchanges():
                for c in self.stats_matrix.all_currencies():
                    self.stats_matrix.set(e, c, cell)

            return self.stats_matrix
        else:
            return self.stats_matrix

class EmaTests:
    def __init__(self, table, decider, parms, vol_percent, plot_steps=False, step_n=int(18e6)):
        self.decider = decider
        self.table = table
        self.parms = parms
        self.plot_steps = plot_steps
        self.vol_percent = vol_percent

        self.step_n = step_n
        self.informer = MongoDataMock()

    def test_historical_data(self):
        decider = self.decider
        trading_currency = decider.trading_currency

        balances = {trading_currency: 2000}
        for c in decider.currencies:
            balances[c] = 0

        volumes = {c: 1 for c in decider.currencies}

        trading_currency_balance_history = []
        total_balance_history = []
        price_history = []
        plt.ion()

        last_offer_type = None


        every = 10000

        beta = 0
        gamma = 0.8
        beta_history = []
        factor_history = []
        avg = None
        beta_price = 0

        for i in range(self.step_n - 1):
            transactions = decider.decide(self.informer)
            price = self.informer.get_stats_matrix(increment=False).get('poloniex', decider.currencies[0]).close
            type = self.informer.get_stats_matrix(increment=False).get('poloniex', decider.currencies[0]).type
            vol = self.informer.get_stats_matrix(increment=False).get('poloniex', decider.currencies[0]).volume

            if type == 'BUY':
                beta = gamma * beta + (1 - gamma) * vol
                beta_price = gamma * beta_price + (1-gamma) * beta * price
            elif type == 'SELL':
                beta = gamma * beta - (1 - gamma) * vol
                beta_price = gamma * beta_price - (1 - gamma) * beta * price

            if avg is None:
                avg = price

            avg = gamma * avg + (1 - gamma) * price

            for t in transactions:
                for d in t.decisions:
                    volume = self.vol_percent * balances[trading_currency] / d.price

                    if d.transaction_type == OfferType.BUY:
                        balances[trading_currency] -= d.price * volume
                        balances[d.base_currency] += volume * 0.998
                        last_offer_type = OfferType.BUY
                        print('Buy', d.price, volume, d.price * volume, balances)
                    else:
                        volume = abs(balances[d.base_currency])
                        balances[trading_currency] += d.price * volume * 0.998
                        balances[d.base_currency] -= volume
                        last_offer_type = OfferType.SELL
                        print('Sell', d.price, volume, d.price * volume, balances)

            if last_offer_type == OfferType.BUY:
                color = 'r'
            else:
                color = 'b'

            balance_in_currencies = balances[trading_currency] + price * balances[decider.currencies[0]]
            if i % int(every) == 0:
                trading_currency_balance_history.append((i, balance_in_currencies, color))
                print(balances)

            if i % every == 0:
                price_history.append((i, price))
                beta_history.append((i, beta_price))
                factor_history.append((i, beta))
                total_balance_history.append((i, balance_in_currencies))

            if self.plot_steps and i % int(every) == 0:
                print('Balances ', balances, ' price ', price)

                self.plot_history(price_history, total_balance_history, trading_currency_balance_history, beta_history, factor_history)

            decider.apply_last()

        file_name = 'reports/%s_%s.png' % (self.table, self.parms)
        open(file_name, 'w+').close()

        self.plot_history(price_history, total_balance_history, trading_currency_balance_history)
        plt.savefig(file_name)

        return trading_currency_balance_history[-1][1]

    def plot_history(self, price_history, total_balance_history, trading_currency_balance_history, beta_history=None, factor_history=None):
        plt.clf()

        # if beta_history is not None:
        #     plt.plot([b[0] for b in beta_history], [0.2*b[1] for b in beta_history], color='b')
        #
        # if factor_history is not None:
        #     plt.plot([b[0] for b in factor_history], [500*b[1] for b in factor_history], color='r')
        #     plt.plot([b[0] for b in factor_history], [0 for b in factor_history], color='g', alpha=0.7)

        # scaled_price_history = price_history / max(price_history)
        # scaled_price_history *= max([b[1] for b in trading_currency_balance_history]) / 2
        scaled_price_history = price_history

        plt.plot([s[0] for s in scaled_price_history], [s[1] for s in scaled_price_history], color='g', alpha=0.7)

        plt.scatter([b[0] for b in trading_currency_balance_history], [b[1] for b in trading_currency_balance_history], color=[b[2] for b in trading_currency_balance_history], marker='^')
        plt.plot([b[0] for b in trading_currency_balance_history], [b[1] for b in trading_currency_balance_history], alpha=0.7)

        # plt.scatter([t[0] for t in total_balance_history], [t[1] for t in total_balance_history], color='b', alpha=0.4)
        plt.pause(0.001)


if __name__ == '__main__':
    trading_currency = 'USDT'
    currency = 'BTC'
    percent = 0.8

    best_parms = None
    best_final_balance = None

    for first_period in [2]:
        for second_period in [5]:
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
                tests = EmaTests('poloniex_%s_%s_5mins_6m_ohlcv' % (currency.lower(), trading_currency.lower()),
                                 decider,
                                 parms, percent, plot_steps=True)
                final_balance = tests.test_historical_data()

                if best_final_balance is None or final_balance > best_final_balance:
                    best_final_balance = final_balance
                    best_parms = parms

                print('Final balance for %s is %f' % (parms, final_balance))

    print('Best parms %s' % str(best_parms))
