from pprint import pprint

from sandbox.utils import get_data_from_db

import matplotlib

matplotlib.use('TkAgg')

from matplotlib.finance import candlestick2_ohlc
import matplotlib.pyplot as plt

import numpy as np
import math

url = 'mongodb://ec2-35-176-249-239.eu-west-2.compute.amazonaws.com'
db_name = 'historicalData'

collection_name_template = 'USDT_%s_7200_1483282414_9999999999'

data = {
    'eth': get_data_from_db(url, db_name, collection_name_template % 'ETH'),
    # 'eth': get_data_from_db(url, db_name, collection_name_template % 'XRP')[-15000:],
    # 'xmr': get_data_from_db(url, db_name, collection_name_template % 'XMR')[-4000:],
    # 'dash': get_data_from_db(url, db_name, collection_name_template % 'DASH')[-4000:],
    # 'ltc': get_data_from_db(url, db_name, collection_name_template % 'LTC')[-4000:],
    # 'zec': get_data_from_db(url, db_name, collection_name_template % 'ZEC')[-4000:]
}

print('Data shape ', data['eth'].shape)

avg_t = 36
candle_t = 4

indicator_values = [0 for _ in range(avg_t + candle_t)]


def relu(x):
    if x <= 0:
        return 0
    else:
        return x


class Position:
    NONE = 1
    LONG = 2
    SHORT = 3


balance = {'eth': 0, 'usd': 10000}
perc = 0.1
position = Position.NONE
position_price = None

balances = []
prices = []

fee = 0.002

for i in range(avg_t + candle_t + 2, data['eth'].shape[0]):
    opens = data['eth'][i - avg_t:i + 1, 0]
    highs = data['eth'][i - avg_t:i + 1, 1]
    lows = data['eth'][i - avg_t:i + 1, 2]
    closings = data['eth'][i - avg_t:i + 1, 3]

    vols = data['eth'][i - avg_t:i + 1, 4]

    avg_vol = np.average(vols[:-candle_t - 1])
    avg_height = np.average(np.abs(opens[:-candle_t - 1] - closings[:-candle_t - 1]))

    before_last_indicators = []
    for j in range(2, candle_t + 1):
        ind_val = relu(data['eth'][i - j, 4] / avg_vol) * (
            (data['eth'][i - j, 3] - data['eth'][i - j, 0]) / avg_height)
        before_last_indicators.append(ind_val)

    before_last_indicator = np.average(before_last_indicators)

    last_value_indicator = ((data['eth'][i - 1, 3] - data['eth'][i - 3, 0]) / avg_height) * \
                           relu(1-data['eth'][i - 1, 4] / avg_vol)
    after_last_value_indicator = ((data['eth'][i - 1, 3] - data['eth'][i - 3, 0]) / avg_height) * \
                           relu(1-data['eth'][i, 4] / avg_vol)

    final_indicator = math.tanh(last_value_indicator + 0.5* before_last_indicator + 0.5*after_last_value_indicator)


    if position != Position.NONE:
        rtrn = position_price / data['eth'][i - 1, 3] - 1
    else:
        rtrn = 0

    INDICATOR_THRESHOLD = 0.8
    WIN_THRESHOLD = 0.05

    fee_factor = (1 - fee)**2

    if position != Position.NONE and rtrn > WIN_THRESHOLD or rtrn < -WIN_THRESHOLD:
        print('Closing position at %f' % data['eth'][i - 1, 3])

        if position == Position.LONG:
            vol = abs(balance['eth'])

            profit = vol * (fee_factor * data['eth'][i - 1, 3] - position_price)
            balance['usd'] += profit
            print('\tProfit %f\n' % profit)
            balance['eth'] = 0
        elif position == Position.SHORT:
            vol = abs(balance['eth'])

            profit = vol * (fee_factor * position_price - data['eth'][i - 1, 3])
            balance['usd'] += profit
            print(fee_factor, '\tProfit %f\n' % profit)
            balance['eth'] = 0

        position = Position.NONE
    elif position == Position.NONE and final_indicator < -INDICATOR_THRESHOLD:
        vol = perc * balance['usd'] / data['eth'][i - 1, 3]

        print('Opening long position at %f with vol %f' % (data['eth'][i - 1, 3], vol))

        balance['eth'] = vol
        position_price = data['eth'][i - 1, 3]
        position = Position.LONG

        # fig, ax = plt.subplots()
        #
        # candlestick2_ohlc(ax,
        #                   opens,
        #                   highs,
        #                   lows,
        #                   closings,
        #                   width=0.7,
        #                   colorup='g',
        #                   colordown='r',
        #                   alpha=0.7)
        #
        # ax.bar([i for i in range(vols.shape[0])], 0.1 * np.average(closings) * vols / np.max(vols))
        #
        # plt.show()
    elif position == Position.NONE and final_indicator > INDICATOR_THRESHOLD:
        vol = perc * balance['usd'] / data['eth'][i - 1, 3]

        print('Opening short position at %f with vol %f' % (data['eth'][i - 1, 3], vol))

        balance['eth'] = -vol
        position_price = data['eth'][i - 1, 3]
        position = Position.SHORT

    if position_price is not None:
        total_balance = balance['usd'] + balance['eth'] * (position_price - data['eth'][i - 1, 3])
        balances.append(total_balance)
        prices.append(data['eth'][i - 1, 3])

    # plt.pause(0.5)

balances = np.array(balances)
prices = np.array(prices)

print(balances[-1])
plt.plot(balances / np.max(balances), color='b', alpha=0.7)
plt.plot(prices / np.max(prices), color='g', alpha=0.7)
plt.show()
