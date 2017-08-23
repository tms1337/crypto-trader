from enum import unique

from service.mq.mqlistener import MQListener
from util.asserting import TypeChecker


@unique
class ServiceActionType(Enum):
    pass


class ServiceAction:
    def __init__(self, msg_id, action_type, parameters):
        TypeChecker.check_type(msg_id, str)
        TypeChecker.check_type(action_type, ServiceActionType)
        TypeChecker.check_type(parameters, dict)

        self.msg_id = msg_id
        self.action_type = action_type
        self.parameters = parameters

class MQDecoder:
    def __init__(self, mqlistener):
        TypeChecker.check_type(mqlistener, MQListener)

        self.mqlistener = mqlistener
        self.mqlistener.start()

    def next(self):
        message = self.mqlistener.next()
        return self._decode(message)

    def _decode(self, message):
        pass
