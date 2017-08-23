from enum import Enum, unique

from manager.botmanager import BotManager
from service.mq.mqdecoder import MQDecoder
from service.mq.mqencoder import MQEncoder
from util.asserting import TypeChecker


class App:
    def __init__(self,
                 bot_manager,
                 encoder,
                 decoder):
        TypeChecker.check_type(bot_manager, BotManager)
        TypeChecker.check_type(encoder, MQEncoder)
        TypeChecker.check_type(decoder, MQDecoder)

        self.bot_manager = bot_manager
        self.encoder = encoder
        self.decoder = decoder

    def run(self):
        while True:
            action = self.decoder.next()

            if not action is None:
                self._do(action)

    def _do(self, action):
        TypeChecker.check_type(action, ServiceAction)
        pass
