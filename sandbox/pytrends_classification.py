import datetime
import json
import urllib.request

import matplotlib
import numpy as np
from pandas import Series
from pytrends.request import TrendReq
from sklearn.model_selection import cross_val_score

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.ensemble import RandomForestRegressor

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


def get_interest_over_time(start, end):
    pytrend = TrendReq()

    pytrend.build_payload(kw_list=['bitcoin price', 'btc usd'], timeframe='%s %s' % (start, end))

    interest_df = pytrend.interest_over_time()

    df_len = len(interest_df['isPartial'])
    interest_df['open'] = Series(np.zeros(df_len), index=interest_df.index)
    interest_df['high'] = Series(np.zeros(df_len), index=interest_df.index)
    interest_df['low'] = Series(np.zeros(df_len), index=interest_df.index)
    interest_df['close'] = Series(np.zeros(df_len), index=interest_df.index)
    interest_df['volume'] = Series(np.zeros(df_len), index=interest_df.index)
    interest_df['hash_power'] = Series(np.zeros(df_len), index=interest_df.index)
    interest_df['miner_revenue'] = Series(np.zeros(df_len), index=interest_df.index)

    return interest_df


second_interest = get_interest_over_time('2016-09-01', '2017-04-01')
third_interest = get_interest_over_time('2017-04-01', '2017-10-23')

second_interest['bitcoin price'] /= third_interest['bitcoin price'][0]
third_interest['bitcoin price'] /= third_interest['bitcoin price'][0]
third_interest = third_interest.iloc[1:]

interest_over_time = pd.concat([second_interest, third_interest])

poloniex_data = json.loads(urllib.request.urlopen(
    "https://poloniex.com/public?command=returnChartData&currencyPair=USDT_BTC&start=1472688000&end=1508781705&period=86400").read().decode(
    'ascii'))

hash_power = {}
with open('/Users/farukmustafic/Downloads/BCHAIN-HRATE.csv') as f:
    lines = f.readlines()
    for line in lines:
        parts = line[:-1].split(',')
        hash_power[parts[0]] = parts[1]

miner_rev = {}
with open('/Users/farukmustafic/Downloads/BCHAIN-MIREV.csv') as f:
    lines = f.readlines()
    for line in lines:
        parts = line[:-1].split(',')
        miner_rev[parts[0]] = parts[1]

for v in poloniex_data:
    date_only = datetime.datetime.fromtimestamp(int(v['date'])).strftime('%Y-%m-%d')
    date_str = date_only + ' 00:00:00'

    interest_over_time.loc[date_str, 'open'] = v['open']
    interest_over_time.loc[date_str, 'high'] = v['high']
    interest_over_time.loc[date_str, 'low'] = v['low']
    interest_over_time.loc[date_str, 'close'] = v['close']
    interest_over_time.loc[date_str, 'volume'] = v['volume']
    interest_over_time.loc[date_str, 'hash_power'] = float(hash_power[date_only])
    interest_over_time.loc[date_str, 'miner_revenue'] = float(miner_rev[date_only])

loc = interest_over_time.loc

trends = loc[:, 'bitcoin price'].values
open = loc[:, 'open'].values
high = loc[:, 'high'].values
low = loc[:, 'low'].values
close = loc[:, 'close'].values
volume = loc[:, 'volume'].values
hashpower = loc[:, 'hash_power'].values
miner_revs = loc[:, 'miner_revenue'].values

fig = plt.figure()
ax = fig.gca()


def calc_emas(arr, days):
    emas = [arr[0]]
    alpha = 2 / (days + 1)
    for t in arr[1:]:
        emas.append((1 - alpha) * emas[-1] + alpha * t)

    emas = np.array(emas)

    return emas


short_period = 7
long_period = 120

emas_short_trends = calc_emas(trends, short_period)

emas_long_trends = calc_emas(trends, long_period)
diff_trends = (emas_short_trends - emas_long_trends) / emas_long_trends

ema_short_volume = calc_emas(volume, short_period)
ema_long_volume = calc_emas(volume, long_period)
diff_volume = (ema_short_volume - ema_long_volume) / ema_long_volume

ema_short_hashrate = calc_emas(hashpower, short_period)
ema_long_hashrate = calc_emas(hashpower, long_period)
diff_hashrate = (ema_short_hashrate - ema_long_hashrate) / ema_long_hashrate

ema_short_miner_rev = calc_emas(miner_revs, short_period)
ema_long_miner_rev = calc_emas(miner_revs, long_period)
diff_miner_rev = (ema_short_miner_rev - ema_long_miner_rev) / ema_long_miner_rev

ema_short_close = calc_emas(close, short_period)
diff_close = np.array([0] + [close[i] / close[i - 1] - 1 for i in range(1, len(close))])


def transform(arr):
    return np.array([1] + list(arr[1:] / arr[:-1] - 1))

# plt.plot(diff_trends, color='r')
# plt.plot(diff_volume, color='g')
# plt.plot(diff_close, color='b')

x = np.column_stack([
    hashpower - ema_short_hashrate,
    volume - ema_short_volume,
    close - ema_short_close
])[:-3]
y = np.array([(close[i] / close[i - 1] - 1) > 0 for i in range(3, close.shape[0])]).astype(int)

print(x.shape, y.shape)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x[:, 0], x[:, 1], x[:, 2], c=y)

plt.gray()
plt.show()

# predictor = Sequential()
# predictor.add(Dense(100, activation='relu', input_shape=x.shape[1:]))
# predictor.add(Dense(1, activation='linear'))
#
# predictor.compile(optimizer=RMSprop(lr=0.000001),
#                   loss='mse',
#                   metrics=[])
#
# predictor.fit(x, y,
#               epochs=1000,
#               batch_size=10,
#               validation_split=0.1,
#               shuffle=True)

regressor = RandomForestRegressor(n_estimators=10, n_jobs=4)
regressor.fit(x, y)

print(cross_val_score(regressor, x, y, n_jobs=4, cv=10))

# plt.plot(np.round(predictor.predict_on_batch(x).flatten(), 0) - y.flatten())
#
# plt.grid()
# plt.show()
