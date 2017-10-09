from pymongo import MongoClient
import numpy as np
import scipy
import scipy.stats
from scipy.stats import cauchy as distribution
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt


mongo_host = 'ec2-52-56-38-131.eu-west-2.compute.amazonaws.com'
mongo_port = 27017

client = MongoClient(mongo_host, mongo_port)
db = client['historicalData']

period = '30min_all'

btc_db = db['poloniex_btc_usdt_%s' % period].find()
eth_db = db['poloniex_eth_usdt_%s' % period].find()
dash_db = db['poloniex_dash_usdt_%s' % period].find()
ltc_db = db['poloniex_ltc_usdt_%s' % period].find()
xmr_db = db['poloniex_xmr_usdt_%s' % period].find()
xrp_db = db['poloniex_xrp_usdt_%s' % period].find()

class MonteCarloDb:
    def __init__(self, distro, mu, sigma, init_price):
        self.distro = distro
        self.mu = mu
        self.sigma = sigma


        for price in ['open', 'high', 'low', 'close']:
            self.curr_price[price] = init_price

    def next(self):
        for price in self.curr_price:
            self.curr_price[price] = self.curr_price[price] * (1 + self.distro.rvs(loc=1.5*self.mu[price], scale=1.5*self.sigma[price]))

        return self.curr_price

def get_montecarlo_db(db, steps, plot=False, init_price=1000):
    retrns = {
        'open': [],
        'high': [],
        'low': [],
        'close': [],
    }

    last_price = None
    for i in range(steps):
        record = db.next()
        o = float(record['open'])
        h = float(record['high'])
        l = float(record['low'])
        c = float(record['close'])

        if last_price is None:
            last_price = {
                'open': o,
                'high': h,
                'low': l,
                'close': c,
            }
        else:
            retrns['open'].append(o / last_price['open'] - 1)
            retrns['high'].append(h / last_price['high'] - 1)
            retrns['low'].append(l / last_price['low'] - 1)
            retrns['close'].append(c / last_price['close'] - 1)

            last_price = {
                'open': o,
                'high': h,
                'low': l,
                'close': c,
            }

    # best fit of data
    mu = {}
    sigma = {}

    for price in ['open', 'high', 'low', 'close']:
        print(distribution.fit(retrns[price]))
        (mu[price], sigma[price]) = distribution.fit(retrns[price])

    print('Fitted', mu, sigma)

    # the histogram of the data
    # n, bins, patches = plt.hist(retrns, 60, normed=1, facecolor='green', alpha=0.75)

    if plot:
        x = np.linspace(-1, 1, 200)
        pdf_fitted = distribution.pdf(x, loc=mu, scale=sigma)

        plt.plot(x, pdf_fitted, 'r-')
        plt.hist(retrns, bins=200, normed=1,alpha=.3)
        plt.show()

    db.rewind()

    return MonteCarloDb(distribution, mu, sigma, init_price=init_price)

btc_mc_db = get_montecarlo_db(btc_db, 45000, init_price=1000)
eth_mc_db = get_montecarlo_db(eth_db, 30000, init_price=1000)
dash_mc_db = get_montecarlo_db(dash_db, 46000, init_price=1000)
xmr_mc_db = get_montecarlo_db(xmr_db, 46000, init_price=1000)
xrp_mc_db = get_montecarlo_db(xrp_db, 45900, init_price=1000)
ltc_mc_db = get_montecarlo_db(ltc_db, 45000, init_price=1000)
