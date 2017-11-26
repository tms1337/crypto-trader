from pprint import pprint

from sklearn.linear_model import LinearRegression

from sandbox.utils import get_data_from_db, get_smas, get_emas

import matplotlib

matplotlib.use('TkAgg')

from matplotlib.finance import candlestick2_ohlc
import matplotlib.pyplot as plt

import numpy as np

url = 'mongodb://ec2-35-176-249-239.eu-west-2.compute.amazonaws.com'
db_name = 'historicalData'

collection_name_template = 'BTC_%s_1800_1493669144_9999999999'

data = {
    'eth': get_data_from_db(url, db_name, collection_name_template % 'ETH'),
    'xrp': get_data_from_db(url, db_name, collection_name_template % 'XRP'),
    'xmr': get_data_from_db(url, db_name, collection_name_template % 'XMR'),
    'dash': get_data_from_db(url, db_name, collection_name_template % 'DASH'),
    'ltc': get_data_from_db(url, db_name, collection_name_template % 'LTC'),
    'zec': get_data_from_db(url, db_name, collection_name_template % 'ZEC')
}

for k,v in data.items():
    split_perc = 0.5
    ind = int(split_perc * v.shape[0])
    train, test = np.split(v, [ind], axis=0)

    data[k] = {'train': train, 'test': test}

def to_returns(v, index=3):
    # v is np array
    return (v[1:, index] - v[:-1, index]) / v[:-1, index]


rtrns = {k: to_returns(v['train']) for k, v in data.items()}
market_returns = np.average(np.vstack([v for _, v in rtrns.items()]), axis=0)

regressor = LinearRegression(fit_intercept=True)
betas = {k: regressor.fit(rtrns[k].reshape(-1, 1), market_returns).coef_[0] for k in rtrns}

pprint(betas)

data_len = None
for _, v in data.items():
    if data_len is None:
        data_len = v['train'].shape[0]
    else:
        assert v['train'].shape[0] == data_len

total_balances = [0 for _ in range(data_len)]

ema_periods = [6, 42]

emas = {}
for k, v in data.items():
    emas[k] = get_emas(v['test'][:, 3], ema_periods)

macd_period = 6
macds = {}
for k, v in emas.items():
    print(v)
    assert len(v) == 2
    macds[k] = get_emas(v[ema_periods[0]] - v[ema_periods[1]], macd_period)

print(macds)

def calc_ranking(k, v, i):
    return (emas[k][6][i] - emas[k][42][i]) / emas[k][42][i]


longs = {k: [] for k in data}
shorts = {k: [] for k in data}

balances = {k: 0 for k in data}
balances['fiat'] = 1000

percent = 1

data_len = data['eth']['test'].shape[0]

prev_positions = None
for i in range(0, data_len, 6):
    rankings = {k: calc_ranking(k, v['test'], i) for k, v in data.items()}
    rankings = sorted(rankings.items(), key=lambda x: x[1], reverse=True)

    positions = {'longs': [rankings[0][0], rankings[1][0]],
                 'shorts': [rankings[-1][0], rankings[-2][0]]}

    # close positions
    if prev_positions is not None:
        for long in prev_positions['longs']:
            balances['fiat'] += abs(balances[long]) * data[long]['test'][i, 3]
            balances[long] = 0

        for short in prev_positions['shorts']:
            balances['fiat'] -= abs(balances[short]) * data[short]['test'][i, 3]
            balances[short] = 0

    for j in range(i, i+6):
        total_balances[j] = balances['fiat']

    if total_balances[i-6] < total_balances[i]:
        percent *= 1.02

        if percent > 2:
            percent = 2
    else:
        percent *= 0.99

        if percent < 0.1:
            percent = 0.1

    print(balances['fiat'], percent)

    for j in positions['longs']:
        longs[j].append(i)
    for j in positions['shorts']:
        shorts[j].append(i)

    fiat_volume = 500

    # open new positions
    for long in positions['longs']:
        balances['fiat'] -= fiat_volume
        balances[long] += fiat_volume / data[long]['test'][i, 3]

    for short in positions['shorts']:
        balances['fiat'] += fiat_volume
        balances[short] -= fiat_volume / data[short]['test'][i, 3]

    prev_positions = positions

fig, ax = plt.subplots()
curr = 0
if False:
    for k, v in data.items():
        plt.sca(ax[curr])

        curr_longs = longs[k]
        curr_shorts = shorts[k]

        # for i in range(0, len(curr_longs)):
        #     long = curr_longs[i]
        #     plt.axvline(long, color='g', alpha=0.5)
        #
        # for i in range(0, len(curr_shorts)):
        #     short = curr_shorts[i]
        #     plt.axvline(short, color='r', alpha=0.5)

        candlestick2_ohlc(ax[curr],
                          v['test'][:, 0],
                          v['test'][:, 1],
                          v['test'][:, 2],
                          v['test'][:, 3],
                          width=0.2)
        for period in ema_periods:
            plt.plot(emas[k][period])

        curr += 1

plt.sca(ax)
plt.plot(total_balances[43:])

plt.show()
