from service.mq.mqwriter import MQWriter
from util.asserting import TypeChecker


class MQEncoder:
    def __init__(self,
                 mqwriter):
        TypeChecker.check_type(mqwriter, MQWriter)

        self.writer = mqwriter

    def error(self, action):
        self.writer.write(action.msg_id, {"error": True})

    def success(self, action, parameters=None):
        if parameters is not None:
            self.writer.write(action.msg_id, {"error": False, "parameters": parameters})
        else:
            self.writer.write(action.msg_id, {"error": False})
