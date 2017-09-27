import os
import numpy as np

from util.mongo import read_mongo


def _get_values(table):
    cache_file_name = 'cache/%s.npy' % table

    if os.path.exists(cache_file_name):
        print('Getting data from cached file')

        values = np.load(cache_file_name)
    else:
        print('Getting data from DB')

        mongo_host = '35.177.25.74'
        mongo_port = 27017

        df = read_mongo('historicalData',
                        table,
                        host=mongo_host,
                        port=mongo_port)
        values = df[['open', 'high', 'low', 'close', 'volume']].values

    np.save(cache_file_name, values)
    print('Got %d datapoints' % values.shape[0])

    return values