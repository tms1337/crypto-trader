from enum import Enum, unique

from manager.botmanager import BotManager
from service.mq.mqdecoder import MQDecoder, ServiceAction
from service.mq.mqencoder import MQEncoder
from util.asserting import TypeChecker
from util.logging import LoggableMixin


class App(LoggableMixin):
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

        LoggableMixin.__init__(self, App)

    def run(self):
        while True:
            try:
                action = self.decoder.next()

                if not action is None:
                    self._do(action)
            except Exception as ex:
                self.logger.error("An error has occured %s" % ex)

    def _do(self, action):
        TypeChecker.check_type(action, ServiceAction)
        pass
