import numpy as np
from scipy.stats import norm as distribution


class MonteCarloDb:
    def __init__(self, distro, mu, sigma, init_price):
        self.distro = distro
        self.mu = mu
        self.sigma = sigma

        self.curr_price = {'volume': 1}
        for price in ['open', 'high', 'low', 'close']:
            self.curr_price[price] = init_price

    def next(self):
        for price in self.curr_price:
            if price != 'volume':
                self.curr_price[price] = self.curr_price[price] * (
                1 + self.distro.rvs(loc=1.5 * self.mu[price], scale=1.5 * self.sigma[price]))

        return self.curr_price

    def batch_size(self, next_size):
        pass


def get_montecarlo_db(db, steps, plot=False, init_price=10000):
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
        plt.hist(retrns, bins=200, normed=1, alpha=.3)
        plt.show()

    db.rewind()

    return MonteCarloDb(distribution, mu, sigma, init_price=init_price)