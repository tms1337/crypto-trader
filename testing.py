from keras.layers import LSTM, Dense, Dropout
from keras.models import Sequential
from keras.losses import categorical_crossentropy, mean_squared_error
from keras.optimizers import Adam
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.model_selection import KFold
import numpy as np
import sys
from sklearn.utils import shuffle
import keras

def load_data(data, seq_len, test_perc):
    for i in range(1, len(data)):
        for j in range(4):
            data[i][j] = (data[i][j] - data[i - 1][3]) / data[i][0]
        data[i][4] = data[i][4] / np.amax(data[:, 4], axis=0)


    data = data[1:]

    sequence_length = seq_len + 1
    x = []
    y = []
    yes = 0
    no = 0
    for i in range(len(data) - sequence_length - 1):
        x.append(data[i: i + sequence_length].reshape(-1))
        # will high price increse compared to last day's close price?
        if data[i + sequence_length][1] >= 1.01 * data[i + sequence_length - 1][3]:
            y.append([0, 1])
            yes += 1
        else:
            y.append([1, 0])
            no += 1

    print("Yes %d\tNo %d" % (yes, no))

    x = np.array(x)
    y = np.array(y)

    x, y = shuffle(x, y)

    divisible_n = 100 * int(x.shape[0] / 100)
    x = x[:divisible_n]
    y = y[:divisible_n]

    test_n = int(test_perc * x.shape[0])
    x_train, x_test = x[:-test_n], x[-test_n:]
    y_train, y_test = y[:-test_n], y[-test_n:]

    return [x_train, y_train, x_test, y_test]


def autoencode(x, y, x_, y_, n_features):
    print(x.shape)
    print(x)

    autoencoder = Sequential()
    autoencoder.add(Dense(2*x.shape[1],
                          input_shape=(x.shape[1],),
                          activation="linear"))
    autoencoder.add(Dense(n_features, activation="softmax"))
    autoencoder.add(Dense(2 * x.shape[1],
                          activation="linear"))
    autoencoder.add(Dense(x.shape[1], activation="softsign"))

    autoencoder.compile(optimizer=Adam(lr=0.001),
                        loss=mean_squared_error,
                        metrics=[keras.metrics.mean_squared_error])
    autoencoder.fit(x, x, batch_size=10, epochs=50)

    return autoencoder.predict(x), autoencoder.predict(y), autoencoder.predict(x_), autoencoder.predict(y_)


df = pd.read_csv(sep=" ",
                 filepath_or_buffer="/data/full_daily_ohlc.csv.reversed")

data = df.values

print("Data loaded")

seq_len = 10
test_perc = 0.3

epochs = 40
batch_size = 10

n_features = 20
x_train, y_train, x_test, y_test = load_data(data, seq_len, test_perc)
x_train, y_train, x_test, y_test = autoencode(x_train, y_train, x_test, y_test, n_features)

print(x_train.shape, y_train.shape)
print(x_test.shape, y_test.shape)

predictor = Sequential()
predictor.add(LSTM(activation="sigmoid",
                   batch_input_shape=(batch_size, x_train.shape[1], x_train.shape[2]),
                   stateful=False,
                   units=30,
                   return_sequences=False,
                   dropout=0.2,
                   recurrent_dropout=0.2))
# predictor.add(LSTM(activation="sigmoid",
#                    return_sequences=True,
#                    units=30,
#                    dropout=0.4))
# predictor.add(LSTM(activation="sigmoid",
#                    return_sequences=False,
#                    units=30,
#                    dropout=0.4))
predictor.add(Dense(50, activation="linear"))
predictor.add(Dropout(0.2))
predictor.add(Dense(2, activation="softmax"))

predictor.compile(optimizer=Adam(lr=0.0000001),
                  loss=categorical_crossentropy,
                  metrics=["accuracy"])

predictor.fit(x_train,
              y_train,
              shuffle=True,
              epochs=epochs,
              batch_size=batch_size)

acc = predictor.evaluate(x_test,
                         y_test,
                         batch_size=batch_size)

print(acc)

eth_pd = pd.read_csv(sep=" ",
                     filepath_or_buffer="/data/full_daily_ohlc.csv.reversed")

eth_data = eth_pd.values

_, _, test_x, test_y = load_data(eth_data, seq_len, 1)
acc = predictor.evaluate(test_x,
                         test_y,
                         batch_size=batch_size)
print("eth acc: %s" % acc)
