import pandas as pd
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from keras.callbacks import TensorBoard
from keras.layers import Dropout
from keras.optimizers import Adam
from pymongo import MongoClient
import numpy as np
from keras.layers import Dense
from keras.models import Sequential
from keras.losses import binary_crossentropy, categorical_crossentropy


def _connect_mongo(host, port, username, password, db):
    """ A util for making a connection to mongo """

    if username and password:
        mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
        conn = MongoClient(mongo_uri)
    else:
        conn = MongoClient(host, port)

    return conn[db]


def read_mongo(db, collection, query=None, host='localhost', port=27017, username=None, password=None, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Connect to MongoDB
    if query is None:
        query = {}
    db = _connect_mongo(host=host, port=port, username=username, password=password, db=db)

    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)

    # Expand the cursor and construct the DataFrame
    df = pd.DataFrame(list(cursor))

    # Delete the _id
    if no_id and '_id' in df:
        del df['_id']

    return df


a, b = 0, 0

def generate_windowed_data(data, window_size):
    global a, b

    windowed_data = []
    y = []
    for i in range(1, data.shape[0] - 3 * window_size - 1):
        curr_chunk = data[i:i + window_size]
        print(i)
        print('Current chunk ', curr_chunk, data[i])

        # curr_chunk /= data[i - 1][3]
        # curr_chunk -= 1

        windowed_data.append(curr_chunk)
        was = False
        for j in range(window_size):
            if data[i + window_size + j][3] > 1.005 * data[i + window_size][3]:
                y.append([0, 1])
                a += 1
                was = True
                break

        if not was:
            y.append([1, 0])
            b += 1

    print('a ', a, 'b: ', b)

    windowed_data = np.array(windowed_data)
    y = np.array(y)

    return windowed_data.reshape((windowed_data.shape[0], -1)), y


mongo_host = "35.177.25.74"
mongo_port = 27017

window_data, window_data_y = None, None
window_size = 10

for table in ['poloniex_ltc_btc_30mins_ohlcv']:
    df = read_mongo('historicalData',
                    table,
                    host=mongo_host,
                    port=mongo_port)
    values = df[['open', 'high', 'low', 'close', 'volume', 'quoteVolume', 'weightedAverage']].values
    print(values)
    x, y = generate_windowed_data(values, window_size)

    if window_data is None:
        window_data = x
        window_data_y = y
    else:
        window_data = np.concatenate([window_data, x])
        window_data_y = np.concatenate([window_data_y, y])

# val_table = 'poloniex_xrp_btc_5mins_ohlcv'
# val_df = read_mongo('historicalData',
#                     val_table,
#                     host=mongo_host,
#                     port=mongo_port)
# val_values = val_df[['open', 'high', 'low', 'close', 'volume', 'quoteVolume', 'weightedAverage']].values
# val_x, val_y = generate_windowed_data(val_values, window_size)

classifier = Sequential()
classifier.add(Dense(100,
                     input_shape=window_data.shape[1:],
                     activation='relu'))
classifier.add(Dense(100))
classifier.add(Dropout(0.5))
classifier.add(Dense(2, activation='softmax'))

classifier.compile(optimizer=Adam(lr=0.000001),
                   loss=categorical_crossentropy,
                   metrics=['accuracy'])
classifier.fit(window_data,
               window_data_y,
               batch_size=50,
               epochs=150,
               # validation_data=(val_x, val_y),
               validation_split=0.1,
               callbacks=[ModelCheckpoint(filepath='/output/checkpoint-{epoch:02d}.hdf5',
                                          mode='auto',
                                          period=1,
                                          save_weights_only=False),
                          TensorBoard(log_dir='/output/logs',
                                      histogram_freq=1,
                                      write_images=True)]
               )



