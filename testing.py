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
    sequence_length = seq_len + 1
    x = []
    y= []
    for i in range(len(data) - sequence_length - 1):
        x.append(data[i: i + sequence_length])
        # will it increase
        if data[i + sequence_length] > data[i + sequence_length - 1]:
            y.append([0, 1])
        else:
            y.append([1, 0])

    x = np.array(x)
    y = np.array(y)

    print(x, y)

    test_n = int(test_perc * x.shape[0])
    x_train, x_test = x[:-test_n], x[test_n:]
    y_train, y_test = y[:-test_n], y[test_n:]

    return [x_train, y_train, x_test, y_test]

df = pd.read_csv(header=None,
                 usecols=[1],
                 filepath_or_buffer="/data/krakenUSD.csv",
                 nrows=int(2e6))

print("Data loaded")
scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))

data = scaler.fit_transform(df.values)

seq_len = 50
test_perc = 0.3

x_train, y_train, x_test, y_test = load_data(data, seq_len, test_perc)


predictor = Sequential()
predictor.add(LSTM(activation="linear",
                   input_dim=1,
                   output_dim=50,
                   return_sequences=True,
                   dropout=0.2))
predictor.add(LSTM(100, activation="linear", return_sequences=False, dropout=0.2))
predictor.add(Dense(20, activation="linear"))
predictor.add(Dropout(0.4))
predictor.add(Dense(2, activation="softmax"))

epochs = 5
batch_size = 100

predictor.compile(optimizer=Adam(lr=0.006),
                  loss=categorical_crossentropy,
                  metrics=["accuracy"])

predictor.fit(x_train,
              y_train,
              epochs=epochs,
              batch_size=batch_size)

predictor.evaluate(x_test,
                   y_test)

