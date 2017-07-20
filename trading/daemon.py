import logging
import random
import time

from trading.strategy.transaction.base import TransactionDecider

from trading.exchange.base import ExchangeWrapperContainer
from trading.strategy.deciders.simple.volume import VolumeDecider


class Daemon:
    def __init__(self,
                 wrapper_container,
                 transaction_deciders,
                 volume_deciders,
                 dt_seconds=60,
                 dt_timeout_seconds=0.5,
                 logger_name="app"):

        pass

    def run(self):
        pass
