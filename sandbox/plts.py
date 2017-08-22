import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import pandas as pd
import numpy as np
import math

df = pd.read_csv(sep=" ",
                 filepath_or_buffer="/home/faruk/Desktop/crpyto-data/eth_daily_ohlc_all.csv")

data = df.values
closing_prices_delta = []
for i in range(1, len(data)):
    closing_prices_delta.append((data[i][3] - data[i - 1][3]) / data[i - 1][3])

print(closing_prices_delta)

plt.hist(closing_prices_delta, bins=200, normed=True)
plt.show()
