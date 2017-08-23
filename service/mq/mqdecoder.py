from enum import unique, Enum

from service.mq.mqlistener import MQListener, ListenerRecord
from util.asserting import TypeChecker

import json

from util.logging import LoggableMixin


@unique
class ServiceActionType(Enum):
    INFO = 1
    SPAWN = 2
    STOP = 3
    PAUSE = 4
    RESUME = 5
    UPDATE = 6


class ServiceAction:
    def __init__(self,
                 msg_id,
                 action_type,
                 bot_id=None,
                 parameters=None):

        if parameters is None:
            parameters = {}

        TypeChecker.check_type(msg_id, str)
        TypeChecker.check_type(action_type, ServiceActionType)
        if not bot_id is None:
            TypeChecker.check_type(bot_id, str)
        TypeChecker.check_type(parameters, dict)

        self.msg_id = msg_id
        self.action_type = action_type
        self.bot_id = bot_id
        self.parameters = parameters


class MQDecoder(LoggableMixin):
    def __init__(self, mqlistener):
        TypeChecker.check_type(mqlistener, MQListener)

        self.mqlistener = mqlistener
        self.mqlistener.start()

        LoggableMixin.__init__(self, MQDecoder)

    def next(self):
        record = self.mqlistener.next()
        return self._decode(record)

    def _decode(self, record):
        TypeChecker.check_type(record, ListenerRecord)

        msg_id = record.key

        value = record.value
        try:
            content = json.loads(value)
            TypeChecker.check_type(content, dict)

            assert "action_type" in content, \
                "action_type field not found in content"
            action_type = content["action_type"]

            if action_type == "info":
                action = self._construct_action(msg_id, content, ServiceActionType.INFO)
            elif action_type == "spawn":
                action = ServiceAction(msg_id, ServiceActionType.SPAWN)
            elif action_type == "pause":
                action = self._construct_action(msg_id, content, ServiceActionType.PAUSE)
            elif action_type == "resume":
                action = self._construct_action(msg_id, content, ServiceActionType.RESUME)
            elif action_type == "update":
                assert "parameters" in content, \
                    "parameters not found when decoding %s" % content
                parameters = content["parameters"]

                action = self._construct_action(msg_id,
                                                content,
                                                ServiceActionType.UPDATE,
                                                parameters)
            else:
                self.logger.warn("Invalid action type %s" % action_type)
                action = None

        except ValueError:
            self.logger.error("Erro while decoding %s" % value)

            action = None
        except AssertionError as ex:
            self.logger.warn("Invalid fields when decoding %s" % value)
            action = None

        return action

    def _construct_action(self, msg_id, content, type, parameters=None):
        assert "id" in content, "id not found in %s" % content
        bot_id = content["id"]

        action = ServiceAction(msg_id, type, bot_id, parameters)

        return action
