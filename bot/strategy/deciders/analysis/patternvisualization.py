from keras.layers import LSTM, RepeatVector, TimeDistributed, Dense
from keras.models import Sequential
from keras.optimizers import Adam
from pymongo import MongoClient
import numpy as np

mongo_host = 'ec2-52-56-38-131.eu-west-2.compute.amazonaws.com'
mongo_port = 27017

client = MongoClient(mongo_host, mongo_port)
db = client['historicalData']
collection = db['poloniex_eth_usdt_5min']

cursor = collection.find()
cursor.batch_size(10 * 10 ** 3)

last_price = 0

buckets = {}
p_init = float(cursor.next()['price'])
prices = []
last_prices = []
inds = []

def get_next_price():
    while True:
        try:
            p = float(cursor.next()['price'])

            if p is not None:
                return p
        except Exception:
            pass

def skip(n):
    for _ in range(n):
        cursor.next()

skip_n = 50
input_len = 1000
output_len = 300

x = []
y = []

for i in range(200):
    print(i)

    input_seq = []
    init_price = get_next_price()

    ema_short = init_price
    gamma_short = (1/21)

    ema_long = init_price
    gamma_long = (1/101)

    ema_super_long = init_price
    gamma_super_long = (1/201)
    for _ in range(input_len):
        price = get_next_price()

        ema_short = (1-gamma_short)*ema_short + gamma_short*price
        ema_long = (1-gamma_long)*ema_long + gamma_long*price
        ema_super_long = (1-gamma_super_long)*ema_super_long + gamma_super_long*price

        record = np.array([price/init_price - 1, ema_short, ema_long, ema_super_long])

        input_seq.append(record)
        skip(skip_n)
    input_seq = np.array(input_seq)
    x.append(np.array(input_seq))

    output_seq = []
    init_price = get_next_price()
    for _ in range(output_len):
        output_seq.append(get_next_price()/init_price - 1)
        skip(skip_n)
    output_seq = np.array(output_seq)
    histogram = np.histogram(output_seq, bins=8, range=(-0.04, 0.04), density=True)

    y.append(0.01 * histogram[0].reshape(-1, 1))

hidden_vec_len = int(input_len * 0.6)
batch_size = 25
time_steps = input_len
features = 4
epochs = 10

x = np.array(x)
y = np.array(y)

model = Sequential()
model.add(LSTM(hidden_vec_len, stateful=False, input_shape=(time_steps, features)))
model.add(RepeatVector(8))
model.add(LSTM(hidden_vec_len, return_sequences=True, stateful=False))
model.add(TimeDistributed(Dense(1, activation='relu')))

model.compile(optimizer=Adam(lr=0.00006),
              loss='mse',
              metrics=['mse'])
model.fit(x, y,
          verbose=1,
          batch_size=batch_size,
          epochs=epochs,
          validation_split=0.1)
