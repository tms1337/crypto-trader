import numpy as np
from pymongo import MongoClient


def get_emas(data, periods):
    emas = {}

    for p in periods:
        emas[p] = calc_ema(data, p)

    return emas


def calc_ema(data, p):
    ema = np.array([0 for _ in range(data.shape[0])]).astype(float)

    ema[0] = data[0]

    curr_ema = ema[0]
    alpha = 1 / (2 * p + 1)

    for i in range(1, data.shape[0]):
        curr_ema = (1 - alpha) * curr_ema + alpha * data[i]

        ema[i] = curr_ema

    return ema


def get_smas(data, periods):
    smas = {}

    for p in periods:
        smas[p] = calc_sma(data, p)

    return smas


def calc_sma(data, period):
    sma = np.array([0 for _ in range(data.shape[0])]).astype(float)

    for i in range(period + 1, data.shape[0]):
        sma[i] = np.average(data[i - period - 1:i + 1])

    return sma


def _connect_mongo(host, port, db):
    conn = MongoClient(host, port)

    return conn[db]


def get_data_from_db(url, db_name, collection_name, port=27017):
    db = _connect_mongo(url, port, db_name)

    data_cursor = db[collection_name].find()
    data = np.array([(d['open'], d['high'], d['low'], d['close'], d['volume']) for d in data_cursor])

    return data
