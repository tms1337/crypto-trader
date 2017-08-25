from service.mq.mqwriter import MQWriter
from util.asserting import TypeChecker
from util.logging import LoggableMixin


class MQEncoder(LoggableMixin):
    def __init__(self,
                 mqwriter):
        TypeChecker.check_type(mqwriter, MQWriter)

        self.writer = mqwriter

        LoggableMixin.__init__(self, MQEncoder)

    def error(self, action, error=None):
        self.logger.info("Writing error for %s %s" % (action, error))

        self.writer.write("+" + action.msg_id, {"success": False})

    def success(self, action, data=None):
        self.logger.info("Writing success for %s" % action)

        if data is not None:
            self.writer.write("+" + action.msg_id, {"success": True, "data": data})
        else:
            self.writer.write("+" + action.msg_id, {"success": True})
