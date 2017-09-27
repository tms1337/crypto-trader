import os

# from keras.callbacks import TensorBoard
# from keras.layers import Dense
# from keras.layers import Dropout
# from keras.losses import categorical_crossentropy
# from keras.models import Sequential
# from keras.optimizers import Adam

from bot.strategy.deciders.analysis.datahelper import _get_values
import numpy as np


def pattern_before(data):
    return True
    if data.shape[0] < 3:
        return False

    return data[-1][4] > data[-2][4] > data[-3][4] and \
        data[-1][3] < data[-2][3] < data[-3][3]


def pattern_after(data):
    price = data[0][3]

    upper_hit, lower_hit = False, False
    upper = price * 1.02
    lower = price * 0.016

    window = 1000

    for i in range(1, min([window, data.shape[0] - 1])):
        high = data[i][1] #max([data[i][0], data[i][3]])
        low = data[i][2] #min([data[i][0], data[i][3]])

        if low < upper < high:
            upper_hit = True

        if low < lower < high:
            lower_hit = True

        # if lower_hit and low < lower * 0.95 < high:
        #     break

        if upper_hit and lower_hit:
            break

    if upper_hit and lower_hit:
        return 2
    elif lower_hit:
        return 0
    elif upper_hit:
        return 1
    else:
        return -1


def get_values_for(currency, trading_currency, verbose=0, period='5mins'):
    if os.path.exists('cache/x-%s-%s.npy' % (currency, trading_currency)):
        print('Getting data from cached file')

        x = np.load('cache/x-%s-%s.npy' % (currency, trading_currency))
        y = np.load('cache/y-%s-%s.npy' % (currency, trading_currency))

        return x, y

    values = _get_values('poloniex_%s_%s_%s_6m_ohlcv' % (currency.lower(), trading_currency.lower(), period))[-20000:]

    x = []
    y = []
    window_len = 10

    only_upper, only_lower, both, none = 0, 0, 0, 0
    for i in range(values.shape[0]):
        percent = (100 * i / values.shape[0])
        if verbose == 1 and percent % 10 == 0:
            print('Finished %d' % percent, 'percent')
        values_before = np.copy(values[:i + 1])
        values_after = np.copy(values[i:])

        if values_before.shape[0] > window_len and pattern_before(values_before):
            closing_price = values_before[-window_len - 1][3]
            closing_volume = values_before[-window_len - 1][4]

            if closing_volume == 0:
                continue

            values_to_append = np.copy(values_before[-window_len:])

            for i in range(4):
                values_to_append[:, i] /= closing_price
                values_to_append[:, i] -= 1

            values_to_append[:, 4] /= closing_volume
            values_to_append[:, 4] -= 1

            x.append(values_to_append)

            after = pattern_after(values_after)

            if after == 2:
                y.append(np.array([1, 0]))
                both += 1
            elif after == 0:
                y.append(np.array([0, 1]))
                only_lower += 1
            elif after == 1:
                y.append(np.array([0, 1]))
                only_upper += 1
            else:
                y.append(np.array([0, 1]))
                none += 1

    pos = both + none
    neg = only_lower + only_upper
    total = pos + neg

    print('None ', none/total)

    print('total: %d, positive %d, negative: %d' % (total, pos, neg))
    print('positive perc: %f, negative perc: %f' % (pos / total, neg / total))

    x = np.array(x)
    x = x.reshape((x.shape[0], -1))
    y = np.array(y)

    np.save('cache/x-%s-%s.npy' % (currency, trading_currency), x)
    np.save('cache/y-%s-%s.npy' % (currency, trading_currency), y)

    return x, y


trading_currency = 'USDT'
currency = 'BTC'

x, y = get_values_for(currency, trading_currency, verbose=1)

train_n = int(0.9 * x.shape[0])
train_x, train_y, test_x, test_y = x[:train_n], y[:train_n], x[train_n:], y[train_n:]

print(x, y)
#
# nn = Sequential()
# nn.add(Dense(100, input_shape=x.shape[1:], activation='relu'))
# nn.add(Dense(50, input_shape=x.shape[1:], activation='relu'))
# # nn.add(Dense(5, input_shape=x.shape[1:], activation='relu'))
# nn.add(Dropout(0.5))
# nn.add(Dense(y.shape[1], activation='softmax'))
#
# nn.compile(optimizer=Adam(0.000006),
#            loss=categorical_crossentropy,
#            metrics=[categorical_crossentropy, 'accuracy'])
# nn.fit(train_x, train_y,
#        sample_weight=np.array([ 1 if e[0] == 1 else 1.2 for e in train_y ]),
#        batch_size=100,
#        epochs=500,
#        verbose=1,
#        shuffle=True,
#        validation_data=(test_x, test_y),
#        callbacks=[
#            TensorBoard(log_dir='./logs', histogram_freq=0, batch_size=100, write_graph=True, write_grads=False,
#                        write_images=False, embeddings_freq=0, embeddings_layer_names=None, embeddings_metadata=None)])
#
x, y = get_values_for('ETH', 'USDT', verbose=1)
# print(x, y)
# print('Evaluation: ', nn.evaluate(x, y))
