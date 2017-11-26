from sandbox.utils import get_data_from_db, get_smas

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.finance import candlestick2_ohlc
import matplotlib.pyplot as plt

data = get_data_from_db(url='mongodb://ec2-35-176-249-239.eu-west-2.compute.amazonaws.com',
                        db_name='historicalData',
                        collection_name='BTC_ETH_14400_1477867508_99999999999')

smas = get_smas(data[:, 3], periods=[6, 42])

def should_long(i):
    return smas[6][i] > smas[6][i-1] and smas[6][i] > 1.01 * smas[42][i]

def should_close_long(i):
    return smas[6][i] < smas[6][i - 1] and smas[6][i] < 1.05 * smas[42][i]


balances = {'fiat': 1000, 'currency': 0}
total_balances = [1000 for _ in range(data.shape[0])]
percent = 0.2
fee = 0.002

buy_points = []
sell_points = []

position, last_price = False, data[43, 3]


def should_short(i):
    return smas[6][i] < 0.99 * smas[42][i]


for i in range(43, data.shape[0]):
    close = data[i, 3]
    if not position and should_long(i):
        volume = (balances['fiat'] * percent) / close

        balances['fiat'] -= close * volume
        balances['currency'] += volume * (1-fee)

        position = True
        last_price = close

        buy_points.append(i)
    elif position and should_close_long(i):
        volume = balances['currency']

        balances['fiat'] += close * volume * (1-fee)
        balances['currency'] -= volume

        position = False

        if close - last_price > 0:
            percent *= 1.2

            if percent > 1:
                percent = 1
        else:
            percent *= 0.3

            if percent < 0.1:
                percent = 0.1

        sell_points.append(i)

    total_balances[i] = balances['fiat'] + balances['currency']*close

fig, ax = plt.subplots(2, 1, sharex=True)

candlestick2_ohlc(ax[0],
                  data[:, 0],
                  data[:, 1],
                  data[:, 2],
                  data[:, 3],
                  width=0.8)

def plot_points(step=100):
    for i in range(0, len(buy_points), step):
        plt.axvline(buy_points[i], color='b', alpha=0.5)
    for i in range(0, len(sell_points), step):
        plt.axvline(sell_points[i], color='r', alpha=0.5)

plt.sca(ax[0])
plt.plot(smas[6], color='r')
plt.plot(smas[42], color='b')
plot_points()

plt.sca(ax[1])
plt.plot(total_balances)
plot_points()

plt.show()