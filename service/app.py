from enum import Enum, unique

from manager.botmanager import BotManager
from service.mq.mqdecoder import MQDecoder, ServiceAction, ServiceActionType
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
                self.logger.error("An error has occured while processing action %s" % ex)

    def _do(self, action):
        TypeChecker.check_type(action, ServiceAction)

        if action.action_type == ServiceActionType.SPAWN:
            assert "type_name" in action.parameters, \
                "Bot type not supplied in %s" % action
            type_name = action.parameters["type_name"]

            try:
                id = self.bot_manager.spawn(type_name, action.parameters)
                self.encoder.success(action, {"id": id})
            except Exception as ex:
                self.encoder.error(action)
                raise ex
        elif action.action_type in [ ServiceActionType.PAUSE, ServiceActionType.STOP, ServiceActionType.RESUME ]:
            assert action.bot_id is not None, \
                "botid for pausing needs to be specified %s" % action

            bot_id = action.bot_id
            TypeChecker.check_type(bot_id, str)

            if self.bot_manager.is_bot_managed(bot_id):
                try:
                    if action.action_type == ServiceActionType.PAUSE:
                        self.bot_manager.pause(bot_id)
                    elif action.action_type == ServiceActionType.STOP:
                        self.bot_manager.stop(bot_id)
                    elif action.action_type == ServiceActionType.RESUME:
                        self.bot_manager.resume(bot_id)

                    self.encoder.success(action)
                except Exception as ex:
                    self.encoder.error(action)
                    raise ex
