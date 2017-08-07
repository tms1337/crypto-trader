from keras.layers import LSTM, Dense
from keras.models import Sequential
from keras.losses import categorical_crossentropy
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.model_selection import KFold
import numpy as np

df = pd.read_csv(header=None,
                 usecols=[1],
                 filepath_or_buffer="/home/faruk/Desktop/.krakenUSD.csv",
                 nrows=100)
print("Data loaded")
plt.plot(df)
plt.show()

scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))
data = pd.DataFrame(scaler.fit_transform(df.values))


def generate_dataset(data):
    data = np.append(data, np.zeros((data.shape[0], 1), dtype=float), axis=1)
    for i in range(data.shape[0] - 1):
        if data[i + 1, 1] > data[i, 0]:
            data[i, 1] = 1
        else:
            data[i, 1] = 0

    return data[0:-1,:]


data = generate_dataset(data)
x = data[:, 0]
print(x.shape)
x = np.reshape(x, (x.shape[0], 1, 1))
y = data[:, 1]
label_binarizer = preprocessing.LabelBinarizer()
label_binarizer.fit(range(2))
y = label_binarizer.transform(y.astype(int))
print(x, y)

predictor = Sequential()
predictor.add(LSTM(activation="linear", units=5, input_shape=(None, 1), return_sequences=False))
predictor.add(Dense(12, activation="linear"))
predictor.add(Dense(2, activation="softmax"))

kf = KFold(n_splits=10)

for train_index, test_index in kf.split(data):
    train_x, train_y = x[train_index], y[train_index]
    test_x, test_y = x[test_index], y[test_index]

    predictor.compile(optimizer="adam",
                      loss=categorical_crossentropy)

    predictor.fit(train_x,
                  train_y,
                  epochs=100,
                  batch_size=10)

    predictor.evaluate(test_x,
                       test_y)
