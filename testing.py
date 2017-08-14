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
from sklearn.utils import shuffle


def load_data(data, seq_len, test_perc):
    for i in range(1, len(data)):
        for j in range(4):
            data[i][j] = (data[i][j] - data[i - 1][3]) / data[i - 1][3]

    data = data[1:]

    sequence_length = seq_len + 1
    x = []
    y = []
    for i in range(len(data) - sequence_length - 1):
        x.append(data[i: i + sequence_length])
        # will high price increse compared to last day's close price?
        if data[i + sequence_length][1] >= 0.05:
            y.append([0, 1])
        else:
            y.append([1, 0])

    x = np.array(x)
    y = np.array(y)

    x, y = shuffle(x, y)

    np.set_printoptions(precision=3)
    print(x)
    print(y)

    divisible_n = 100 * int(x.shape[0] / 100)
    x = x[:divisible_n]
    y = y[:divisible_n]

    test_n = int(test_perc * x.shape[0])
    x_train, x_test = x[:-test_n], x[-test_n:]
    y_train, y_test = y[:-test_n], y[-test_n:]

    return [x_train, y_train, x_test, y_test]


df = pd.read_csv(sep=" ",
                 filepath_or_buffer="/data/full_daily_ohlc.csv.reversed")

data = df.values

print("Data loaded")

seq_len = 10
test_perc = 0.3

epochs = 20
batch_size = 10

x_train, y_train, x_test, y_test = load_data(data, seq_len, test_perc)

print(x_train.shape, y_train.shape)
print(x_test.shape, y_test.shape)

predictor = Sequential()
predictor.add(LSTM(activation="sigmoid",
                   batch_input_shape=(batch_size, x_train.shape[1], x_train.shape[2]),
                   stateful=False,
                   units=50,
                   return_sequences=True,
                   dropout=0.2,
                   recurrent_dropout=0.2))
predictor.add(LSTM(activation="sigmoid",
                   return_sequences=False,
                   units=20,
                   dropout=0.2))
predictor.add(Dense(30, activation="linear"))
predictor.add(Dropout(0.2))
predictor.add(Dense(20, activation="linear"))
predictor.add(Dense(2, activation="softmax"))

predictor.compile(optimizer=Adam(lr=0.00003),
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
# print(x_test[-batch_size:])
# print(predictor.predict_proba(x_test, batch_size=batch_size))
# print(predictor.predict_on_batch(x_test[-batch_size:]))
