import random

from pymongo import MongoClient
import numpy as np

import matplotlib

from sandbox.utils import _connect_mongo, get_data_from_db

matplotlib.use('TkAgg')

from matplotlib.finance import candlestick2_ohlc
import matplotlib.pyplot as plt

data = get_data_from_db(url='mongodb://ec2-35-176-249-239.eu-west-2.compute.amazonaws.com',
                        db_name='historicalData',
                        collection_name='USDT_BTC_14400_1477867508_99999999999')

print('Data shape', data.shape)

sma_5 = np.array([0 for _ in range(data.shape[0])])
sma_8 = np.array([0 for _ in range(data.shape[0])])
sma_13 = np.array([0 for _ in range(data.shape[0])])
sma_34 = np.array([0 for _ in range(data.shape[0])])
awesome_oscillator = np.array([0 for _ in range(data.shape[0])])


def calc_smma(i, smas, period):
    midpoints = 0.5 * (data[i - period + 1:i + 1, 1] + data[i - period + 1:i + 1, 2])

    return np.average(midpoints)


sma_5[13] = np.average(0.5 * (data[14 - 5:14, 1] + data[14 - 5:14, 2]))
sma_8[13] = np.average(0.5 * (data[14 - 8:14, 1] + data[14 - 8:14, 2]))
sma_13[13] = np.average(0.5 * (data[14 - 13:14, 1] + data[14 - 13:14, 2]))

for i in range(35, data.shape[0]):
    sma_5[i] = calc_smma(i, sma_5, 5)
    sma_8[i] = calc_smma(i, sma_8, 8)
    sma_13[i] = calc_smma(i, sma_13, 13)

    sma_34[i] = calc_smma(i, sma_34, 34)

    awesome_oscillator[i] = sma_5[i] - sma_34[i]


def is_fractal_high(i):
    high = data[i, 1]
    low = data[i, 2]

    return data[i - 1, 1] < high and \
           data[i - 2, 1] < high and \
           data[i + 1, 1] < high and \
           data[i + 2, 1] < high and \
           low > sma_8[i]


def is_fractal_low(i):
    low = data[i, 2]

    return data[i - 2, 2] > low and \
           data[i - 1, 2] > low and \
           data[i + 1, 2] > low and \
           data[i + 2, 2] > low and \
           low < sma_8[i]


def calc_order(beg):
    aligator = np.array([sma_5[beg], sma_8[beg], sma_13[beg]])

    return np.argsort(aligator)


def lines_didnt_cross(beg, end):
    order = calc_order(beg)

    for i in range(beg + 1, end + 1):
        if not np.all(calc_order(i) == order):
            return False

    return True


def buy_signal(i):
    should_buy = is_fractal_high(i - 5) and \
                 not is_fractal_low(i) and \
                 not is_fractal_low(i - 1) and \
                 not is_fractal_low(i - 2) and \
                 not is_fractal_low(i - 3) and \
                 not is_fractal_low(i - 4) and \
                 data[i, 2] > sma_8[i] and \
                 data[i - 1, 2] > sma_8[i - 1] and \
                 data[i - 2, 2] > sma_8[i - 2] and \
                 data[i - 3, 2] > sma_8[i - 3] and \
                 data[i - 4, 2] > sma_8[i - 4] and \
                 lines_didnt_cross(i - 5, i)

    price = data[i - 5, 1]

    return should_buy, price


def sell_signal(i):
    return not lines_didnt_cross(i, i + 1)


buy_points, sell_points = [], []

initial_fiat_balance = 1000
balances = {'fiat': initial_fiat_balance, 'currency': 0}
volume = 1
total_balances = [initial_fiat_balance for _ in range(data.shape[0])]

position = False
for i in range(34 + 5, data.shape[0] - 2):
    buy_params = buy_signal(i)

    if not position and buy_params[0]:
        # buy
        buy_points.append(i)
        position = True

        balances['fiat'] -= volume * data[i, 3]
        balances['currency'] += volume
    elif position and sell_signal(i):
        # sell
        sell_points.append(i)
        position = False

        balances['fiat'] += volume * data[i, 3]
        balances['currency'] -= volume

    total_balances[i] = balances['fiat'] + data[i, 3] * balances['currency']

print(balances)

fig, ax = plt.subplots(3, 1, sharex=True)

candlestick2_ohlc(ax[0],
                  data[:, 0],
                  data[:, 1],
                  data[:, 2],
                  data[:, 3],
                  width=0.5)

plt.sca(ax[0])
plt.plot(sma_5)
plt.plot(sma_8)
plt.plot(sma_13)

step = 1


def plot_points():
    for i in range(0, len(buy_points), step):
        plt.axvline(buy_points[i], color='b', alpha=0.5)
    for i in range(0, len(sell_points), step):
        plt.axvline(sell_points[i], color='r', alpha=0.5)


# plot_points()

awesome_colors = ['g' if i == 0 or awesome_oscillator[i] > awesome_oscillator[i - 1] else 'r' for i in
                  range(len(awesome_oscillator))]
plt.sca(ax[1])
plt.bar([i for i in range(len(awesome_oscillator))], awesome_oscillator, color=awesome_colors)
# plot_points()

plt.sca(ax[2])
plt.plot(total_balances)

plt.show()
