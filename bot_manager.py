import logging
import sys


from bot.exchange.bittrex.stats import BittrexStatsProvider
from bot.exchange.bittrex.trade import BittrexTradeProvider

from manager.botmanager import BotManager
from percentbased import PercentBotType
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

manager = BotManager()

manager.add_bot_type(PercentBotType)

app = App(bot_manager=manager,
          encoder=MQEncoder(mqwriter=KafkaWriter(topic="test")),
          decoder=MQDecoder(mqlistener=KafkaListener(topic="test")))
app.run()
