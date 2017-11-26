from sandbox.utils import get_data_from_db, get_smas

import matplotlib

matplotlib.use('TkAgg')

from matplotlib.finance import candlestick2_ohlc
import matplotlib.pyplot as plt

import numpy as np

url = 'mongodb://ec2-35-176-249-239.eu-west-2.compute.amazonaws.com'
db_name = 'historicalData'

begin_date = '1446599066'
end_date = '9999999999'

collection_name_template = (('%s_%s_86400_') + begin_date + '_' + end_date)

data = {
    'eth': get_data_from_db(url, db_name, collection_name_template % ('BTC', 'ETH')),
    'xrp': get_data_from_db(url, db_name, collection_name_template % ('BTC', 'XRP')),
    'xmr': get_data_from_db(url, db_name, collection_name_template % ('BTC', 'XMR')),
    'dash': get_data_from_db(url, db_name, collection_name_template % ('BTC', 'DASH')),
    'ltc': get_data_from_db(url, db_name, collection_name_template % ('BTC', 'LTC')),
    'btc': get_data_from_db(url, db_name, collection_name_template % ('USDT', 'BTC'))
}


def to_returns(v, index=3):
    # v is np array
    return (v[1:, index] - v[:-1, index]) / v[:-1, index]


data = {k: to_returns(v) for k, v in data.items()}

market_returns = np.average(np.vstack([v for _, v in data.items()]), axis=0)

plt.plot(market_returns, color='b', alpha=0.5)
plt.plot([0 for _ in range(len(market_returns))], color='r')
plt.show()

for k, v in data.items():
    plt.title('%s response to market returns' % k)
    plt.scatter(market_returns, v)
    plt.show()
