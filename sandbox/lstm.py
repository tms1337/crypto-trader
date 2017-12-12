import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

tick_n = 10**6

prices = []
with open('/Users/farukmustafic/workspace/crypto-data') as f:
    cnt = 0
    for line in f:
        price = line.split()[4]

        prices.append(price)

        cnt += 1

        if cnt == tick_n:
            break

prices = np.array(prices, dtype=float)

past_window = 10000

initial_balance = 1000

balance = {'usd': initial_balance, 'btc':0}
total_balances = [initial_balance for _ in range(past_window)]
last_price = None
vol = 0.1

williams_rs = [0 for _ in range(past_window)]
for i in range(past_window+1, prices.shape[0] - 1):
    past = prices[i-past_window:i].astype(float)

    highest_high = np.max(past)
    lowest_low = np.min(past)

    price = prices[i]

    williams_r = 100*(highest_high - price) / (highest_high - lowest_low)
    williams_rs.append(williams_r)

    if williams_r > 80:
        #buy
        balance['usd'] -= vol * price
        balance['btc'] += vol
    elif williams_r < 20:
        #sell
        balance['usd'] += vol * price
        balance['btc'] -= vol

    last_price = price

    total_balances.append(balance['usd'] + balance['btc']*price)

plt.plot(prices)
plt.plot(williams_rs)
plt.plot(total_balances)
plt.show()

exit(0)

# x, y = [], []
#
# past_window = 10000
# future_window = 5000
# for i in range(prices.shape[0] - 1 - past_window - future_window):
#     x.append(prices[i:i + past_window])
#
#     future = prices[i + past_window:i + past_window + future_window].astype(float)
#     print('Future shape', future.shape)
#     max_val = np.max(future)
#     min_val = np.min(future)
#
#     mu = (max_val + min_val) / 2
#     sigma = (max_val - min_val) / 2
#
#     y.append([mu, sigma])
#
# x = np.array(x)
# y = np.array(y)
#
# should_plot = False
#
# if should_plot:
#     f, (ax1, ax2) = plt.subplots(1, 2, sharey=False)
#     ax1.plot(y[:, 0], color='b', alpha=0.5)
#     ax2.plot(y[:, 1], color='r', alpha=0.5)
#
#     plt.show()
#
# params = {'n_estimators': 500, 'max_depth': 4, 'min_samples_split': 2,
#           'learning_rate': 0.01, 'loss': 'ls'}
# clf = ensemble.GradientBoostingRegressor(**params)
#
#
# def monitor(i, self, local):
#   y_score_gen = self.staged_predict_proba(x)
#   y_score = []
#   for y in y_score_gen:
#     y_score = y[:,0]
#     break
#   #y_score is the same each iteration
#   print(y_score)
#
# clf.fit(x, y, monitor=monitor)
#