import logging
import sys


from bot.exchange.bittrex.stats import BittrexStatsProvider
from bot.exchange.bittrex.trade import BittrexTradeProvider

from manager.botmanager import BotManager
from sandbox.percentbased import PercentBotType
from service.app import App
from service.mq.kafka.kafkalistener import KafkaListener
from service.mq.kafka.kafkawriter import KafkaWriter
from service.mq.mqdecoder import MQDecoder
from service.mq.mqencoder import MQEncoder


logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler('debug.log')
fh.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter(fmt="[%(threadName)s / %(asctime)s / %(name)s / %(levelname)s / %(funcName)s]\t"
                                  "%(message)s", datefmt="%Y-%m-%d,%H:%M")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

providers_pause_dt = 0.5

keys_path = "/home/faruk/Desktop/production_keys/"

parameters = {}

parameters["stats_providers"] = {
    # "poloniex": PoloniexStatsProvider(pause_dt=providers_pause_dt),
    "bittrex": BittrexStatsProvider(pause_dt=providers_pause_dt),
    # "bitfinex": BitfinexStatsProvider(),
    # "kraken": KrakenStatsProvider()
}
parameters["trade_providers"] = {
    # "poloniex": PoloniexTradeProvider(key_uri=("%s/poloniex" % keys_path), pause_dt=providers_pause_dt),
    "bittrex": BittrexTradeProvider(key_uri=("%s/bittrex" % keys_path), pause_dt=providers_pause_dt),
    # "bitfinex": BitfinexTradeProvider(key_uri=("%s/bitfinex" % keys_path)),
    # "kraken": KrakenTradeProvider(key_uri=("%s/kraken" % keys_path))
}
parameters["daemon_dt"] = 60
parameters["currencies_for_crypto"] = ["ETH", "LTC", "DASH"]
parameters["trading_currency_for_crypto"] = "BTC"
parameters["crypto_values"] = {"ETH": 10, "DASH": 10, "LTC": 50}
parameters["short_buy_threshold"] = 0.005
parameters["short_sell_threshold"] = 0.01
parameters["short_security_loss_threshold"] = 0.2
parameters["long_buy_threshold"] = 0.01
parameters["long_sell_threshold"] = 0.05
parameters["long_security_loss_threshold"] = 0.2

print(parameters)

manager = BotManager()

manager.add_bot_type(PercentBotType)

app = App(bot_manager=manager,
          encoder=MQEncoder(mqwriter=KafkaWriter(topic="test")),
          decoder=MQDecoder(mqlistener=KafkaListener(topic="test")))
app.run()
