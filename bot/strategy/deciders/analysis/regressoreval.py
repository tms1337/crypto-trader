from keras.models import load_model
from pymongo import MongoClient
import numpy as np

mode = 'single'

mongo_host = 'ec2-52-56-38-131.eu-west-2.compute.amazonaws.com'
mongo_port = 27017

client = MongoClient(mongo_host, mongo_port)
db = client['historicalData']

btc_db = db['poloniex_btc_usdt_5min'].find()
eth_db = db['poloniex_eth_usdt_5min'].find()
etc_db = db['poloniex_etc_usdt_5min'].find()
dash_db = db['poloniex_dash_usdt_5min'].find()

btc_regressor = load_model('/btc/model.h5')
eth_regressor = load_model('/eth/model.h5')
etc_regressor = load_model('/ethc/model.h5')
dash_regressor = load_model('/dash/model.h5')

time_steps = 12 * 24 * 5
future_time_steps = 12 * 12
features = 5

# skip training steps
data_n = 40 * (time_steps + future_time_steps)
btc_db.skip(data_n)
eth_db.skip(data_n)
etc_db.skip(data_n)
dash_db.skip(data_n)

def get_ohlcv(cursor):
    record = cursor.next()

    o = float(record['open'])
    h = float(record['high'])
    l = float(record['low'])
    c = float(record['close'])
    v = float(record['volume'])

    return o, h, l, c, v

def get_expected_return(db, regressor):
    btc_x = []

    _, _, _, close_init, _ = get_ohlcv(db)

    for j in range(time_steps):
        o, h, l, c, v = get_ohlcv(db)

        btc_x.append(np.array([o, h, l, c, v]))

    last_price = btc_x[-1][3]
    btc_x = np.array(btc_x)
    btc_x /= close_init
    btc_x[4] *= close_init
    btc_x[4] /= 1000
    btc_x -= 1

    expected_return = regressor.predict_on_batch(np.array([btc_x]))[0]

    return expected_return, last_price

fee = 0.002

if mode == 'single':
    #btc test

    total = 0
    per_trade = 50000

    totals = []

    step = 12 * 6 # hourly

    data_n = 40 * 10**3

    data = []
    for i in range(data_n):
        if (i + 1) % 1000 == 0:
            print(i + 1, '/', data_n)

        ohlcv_record = btc_db.next()

        open = float(ohlcv_record['open'])
        high = float(ohlcv_record['high'])
        low = float(ohlcv_record['low'])
        close = float(ohlcv_record['close'])
        volume = float(ohlcv_record['volume'])

        data.append(np.array([open, high, low, close, volume]))

    data = np.array(data)

    i = 1
    while i < data.shape[0] - time_steps - future_time_steps - 1:
        curr_frame = np.array(data[i:i + time_steps])

        curr_frame /= data[i - 1][3]
        curr_frame[4] *= data[i - 1][3]

        curr_frame[4] /= 1000

        curr_frame -= 1
        curr_frame[4] += 1

        trade_price = data[i + time_steps - 1][3]
        final_price = data[i + time_steps + future_time_steps][3]

        expected_return = btc_regressor.predict_on_batch(np.array([curr_frame]))[0]

        if expected_return < 0:
            total -= per_trade * (final_price - trade_price)
        else:
            total += per_trade * (final_price - trade_price)

        # total -= fee * (trade_price + final_price)

        print('\t', trade_price, final_price, expected_return)
        print(total)

        i += step


elif mode == 'all':
    # long short equity
    total = 0
    per_trade = 1000

    totals = []
    for i in range(500):
        btc_return, btc_price = get_expected_return(btc_db, btc_regressor)
        eth_return, eth_price = get_expected_return(eth_db, eth_regressor)
        etc_return, etc_price = get_expected_return(etc_db, etc_regressor)
        dash_return, dash_price = get_expected_return(dash_db, dash_regressor)

        sorted_returns = sorted(list(enumerate( [btc_return, eth_return, etc_return, dash_return] )),
                                key=lambda x: x[1],
                                reverse=True)

        actions = [1, 1, 1, 1]

        if btc_return < 0:
            actions[0] *= -1

        if eth_return < 0:
            actions[1] *= -1

        if etc_return < 0:
            actions[2] *= -1

        if dash_return < 0:
            actions[3] *= -1

        for j in range(future_time_steps):
            btc_db.next()
            eth_db.next()
            etc_db.next()
            dash_db.next()

        _, _, _, btc_close, _ = get_ohlcv(btc_db)
        _, _, _, eth_close, _ = get_ohlcv(eth_db)
        _, _, _, etc_close, _ = get_ohlcv(etc_db)
        _, _, _, dash_close, _ = get_ohlcv(dash_db)

        total += per_trade * (btc_close/btc_price - 1) * actions[0] - fee * (btc_close + btc_price)
        total += per_trade * (eth_close/eth_price - 1) * actions[1] - fee * (eth_close + eth_price)
        total += per_trade * (etc_close/etc_price - 1) * actions[2] - fee * (etc_close + etc_price)
        total += per_trade * (dash_close/dash_price - 1) * actions[3] - fee * (dash_close + dash_price)

        print(total)
        totals.append(total)

    print(totals)
