from trading.kraken.providers.trade import TradeProvider
from trading.kraken.providers.stats import StatsProvider
import time

trader = TradeProvider(base_currency="XRP",
                       quote_currency="EUR",
                       key_uri="/home/faruk/Desktop/key")

stats = StatsProvider(base_currency="XRP",
                      quote_currency="EUR")

while True:
    print(stats.last_ohlc())
    time.sleep(5)