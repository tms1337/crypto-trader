import os
import random
import sys

from keras.backend import categorical_crossentropy
from keras.callbacks import TensorBoard, ModelCheckpoint
from keras.layers import LSTM, Dense, Dropout, RepeatVector, TimeDistributed, Flatten
from keras.models import Sequential, load_model
from keras.optimizers import Adam
from pymongo import MongoClient
import numpy as np


mongo_host = 'ec2-52-56-38-131.eu-west-2.compute.amazonaws.com'
mongo_port = 27017

client = MongoClient(mongo_host, mongo_port)
db = client['historicalData']

btc_db = db['poloniex_btc_usdt_5min'].find()
eth_db = db['poloniex_eth_usdt_5min'].find()
etc_db = db['poloniex_etc_usdt_5min'].find()
dash_db = db['poloniex_dash_usdt_5min'].find()
ltc_db = db['poloniex_ltc_usdt_5min'].find()
xmr_db = db['poloniex_xmr_usdt_5min'].find()
xrp_db = db['poloniex_xrp_usdt_5min'].find()

dbs = [btc_db, eth_db, etc_db, dash_db, ltc_db, xmr_db, xrp_db]

local = 'LOCAL' in os.environ
mode = sys.argv[1]

def get_ohlcv(cursor):
    record = cursor.next()

    o = float(record['open'])
    h = float(record['high'])
    l = float(record['low'])
    c = float(record['close'])
    v = float(record['volume'])

    return o, h, l, c, v

data_n = 70 * 10**3

before_len = int(12*8*24)
after_len = int(12*8)
features = 3

if mode == 'testing':
    additional_skip = 0

    total_skip = data_n + additional_skip

    for db in dbs:
        db.skip(total_skip)

    agent = load_model('/models/model.h5')

    data_n = 105000 - data_n - additional_skip
elif mode == 'training':
    agent = Sequential()
    agent.add(LSTM(100,
                   input_shape=(before_len, features*len(dbs)),
                   dropout=0.2,
                   recurrent_dropout=0.2,
                   return_sequences=False))
    # agent.add(LSTM(100, return_sequences=False))
    agent.add(Dense(20, activation='relu'))
    # agent.add(Dense(20, activation='relu'))
    agent.add(Dropout(0.2))
    agent.add(Dense(len(dbs) + 1, activation='softmax'))

    agent.compile(optimizer=Adam(lr=0.0006),
                  loss=categorical_crossentropy,
                  metrics=[])

data = []
for i in range(data_n):
    if i % (10 * 10**3) == 0:
        print(i, '/', data_n)

    feature_vector = []

    for db in dbs:
        o, h, l, c, v = get_ohlcv(db)
        feature_vector.append(c)
        feature_vector.append(h)
        feature_vector.append(l)

    data.append(feature_vector)

data = np.array(data)

x = []
y = []

step = int(0.1 * before_len)
if mode == 'testing':
    step = before_len

for i in range(0, data.shape[0] - before_len - after_len, step):
    state = np.copy( data[i:i+before_len] )
    state[:-1] /= state[-1]

    state_after = np.copy(data[i + before_len - 1 + after_len, 1::features])
    state_after /= state[-1, 1::features]

    if mode == 'testing':
        print('state_after(data_creation)', state_after)

    state_after -= 1

    # state_after = np.exp(100*state_after)
    # state_after /= sum(state_after)

    if mode == 'testing':
        print('\tstate_after_softmax', state_after)

    state_after = np.insert(state_after, 0, 0, axis=0)

    state[-1] /= state[-1]

    if local:
        print(state)
        print(state_after)

    x.append(state)
    y.append(state_after)

x = np.array(x)
y = np.array(y)

if mode == 'testing':

    total = 10 * 10**3
    totals = [total]
    for i in range(x.shape[0]):
        state = x[i]
        state_after = y[i]

        allocation = agent.predict_on_batch(np.array([state]))[0]

        if random.random() < 0.5:
            print('Allocation ', allocation)
            print('state_after ', state_after)

        total_percent_allocated = np.sum(allocation)

        total = (1 - total_percent_allocated) * total + \
                sum(allocation[1:] * (1 + state_after[1:])) * total

        totals.append(total)

    print('Agent totals ', totals)

    total = 10 * 10**3
    totals = []
    for i in range(x.shape[0]):
        state = x[i]
        state_after = y[i]

        allocation = np.array([1/len(dbs) for i in range(len(dbs) + 1)])
        allocation[0] = 0

        total_percent_allocated = np.sum(allocation)

        total = (1 - total_percent_allocated) * total + \
                sum(allocation[1:] * (1 + state_after[1:])) * total

        totals.append(total)

    print('Uniform b&h totals ', totals)

elif mode == 'training':
    agent.fit(x, y,
              batch_size=250,
              epochs=1000,
              validation_split=0.1,
              shuffle=True,
              callbacks=[TensorBoard(log_dir='/output/logs',
                                    batch_size=10),
                         ModelCheckpoint('/output/model.h5', period=1)])
