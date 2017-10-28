import matplotlib
from keras.layers import LSTM, Dense
from keras.models import Sequential
from keras.optimizers import Adam

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from sklearn import ensemble

tick_n = 100000

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

x, y = [], []

past_window = 10000
future_window = 5000
for i in range(prices.shape[0] - 1 - past_window - future_window):
    x.append(prices[i:i + past_window])

    future = prices[i + past_window:i + past_window + future_window].astype(float)
    print('Future shape', future.shape)
    max_val = np.max(future)
    min_val = np.min(future)

    mu = (max_val + min_val) / 2
    sigma = (max_val - min_val) / 2

    y.append([mu, sigma])

x = np.array(x)
y = np.array(y)

should_plot = False

if should_plot:
    f, (ax1, ax2) = plt.subplots(1, 2, sharey=False)
    ax1.plot(y[:, 0], color='b', alpha=0.5)
    ax2.plot(y[:, 1], color='r', alpha=0.5)

    plt.show()

params = {'n_estimators': 500, 'max_depth': 4, 'min_samples_split': 2,
          'learning_rate': 0.01, 'loss': 'ls'}
clf = ensemble.GradientBoostingRegressor(**params)


def monitor(i, self, local):
  y_score_gen = self.staged_predict_proba(x)
  y_score = []
  for y in y_score_gen:
    y_score = y[:,0]
    break
  #y_score is the same each iteration
  print(y_score)

clf.fit(x, y, monitor=monitor)

exit(0)

regressor = Sequential()
regressor.add(LSTM(units=10,
                   input_shape=x.shape[1:],
                   return_sequences=False,
                   stateful=False))
regressor.add(Dense(50, activation='relu'))
regressor.add(Dense(2, activation='relu'))

regressor.compile(optimizer=Adam(lr=0.0006),
                  loss='mse')
regressor.fit(x, y,
              epochs=50,
              shuffle=True,
              batch_size=100,
              validation_split=0.1)

for i in range(x.shape[0]):
    prediction = regressor.predict_on_batch([x[i:i + 1]])[0]

    print(prediction, y[i])

    plt.plot(x[i][0])
    plt.show()
