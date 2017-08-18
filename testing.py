from keras.layers import LSTM, Dense, Dropout
from keras.models import Sequential
from keras.losses import categorical_crossentropy
from keras.optimizers import Adam
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.model_selection import KFold
import numpy as np
import sys


def load_data(data, seq_len, test_perc):
    for i in range(1, len(data)):
        for j in range(5):
            data[i][j] = (data[i][j] - data[i - 1][j]) / data[i - 1][j]

    data = data[1:]

    sequence_length = seq_len + 1
    x = []
    y = []
    for i in range(len(data) - sequence_length - 1):
        x.append(data[i: i + sequence_length])
        # will it increase
        if data[i + sequence_length][1] > data[i + sequence_length - 1][3]:
            y.append([0, 1])
        else:
            y.append([1, 0])

    x = np.array(x)
    y = np.array(y)

    divisible_n = 100 * int(x.shape[0] / 100)
    x = x[:divisible_n]
    y = y[:divisible_n]

    test_n = int(test_perc * x.shape[0])
    x_train, x_test = x[:-test_n], x[-test_n:]
    y_train, y_test = y[:-test_n], y[-test_n:]

    return [x_train, y_train, x_test, y_test]

def autoencode(x, y, x_, y_, n_features):
    autoencoder = Sequential()

    autoencoder.add(Dense(10, input_shape=x.shape[1:],
                          activation="linear"))
    autoencoder.add(Dense(n_features, activation="sigmoid"))
    autoencoder.add(Dense(10, activation="linear"))

    autoencoder.fit(x, x, batch_size=10, epochs=10, validation_data=(x_, y_))

    return autoencoder.predict(x), autoencoder.predict(y), autoencoder.predict(x_), autoencoder.predict(y_)

df = pd.read_csv(sep=" ",
                 filepath_or_buffer="/data/full_daily_ohlc.csv.reversed")

data = df.values

print("Data loaded")

seq_len = 50
test_perc = 0.3

epochs = 1
batch_size = 10

n_features = 10
x_train, y_train, x_test, y_test = load_data(data, seq_len, test_perc)
x_train, y_train, x_test, y_test = autoencode(x_train, y_train, x_test, y_test, n_features)


print(x_train.shape, y_train.shape)
print(x_test.shape, y_test.shape)

predictor = Sequential()
predictor.add(LSTM(activation="linear",
                   batch_input_shape=(batch_size, x_train.shape[1], x_train.shape[2]),
                   stateful=False,
                   units=100,
                   return_sequences=True,
                   dropout=0.5,
                   recurrent_dropout=0.5))
predictor.add(LSTM(activation="linear",
                   return_sequences=False,
                   units=100))
predictor.add(Dense(200, activation="linear"))
predictor.add(Dropout(0.5))
predictor.add(Dense(100, activation="linear"))
predictor.add(Dropout(0.5))
predictor.add(Dense(20, activation="linear"))
predictor.add(Dropout(0.5))
predictor.add(Dense(2, activation="softmax"))

predictor.compile(optimizer=Adam(lr=0.00001),
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
print(x_test[-batch_size:])
print(predictor.predict_proba(x_test[-batch_size:], batch_size=batch_size))
print(predictor.predict_on_batch(x_test[-batch_size:]))
