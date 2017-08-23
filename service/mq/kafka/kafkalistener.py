from service.mq.mqlistener import MQListener, ListenerRecord
from kafka import KafkaConsumer

from util.asserting import TypeChecker
from util.logging import LoggableMixin


class KafkaListener(MQListener, LoggableMixin):
    def __init__(self,
                 topic,
                 host="localhost",
                 port=9092):
        TypeChecker.check_type(topic, str)
        TypeChecker.check_type(host, str)
        TypeChecker.check_type(port, int)

        self.consumer = KafkaConsumer(topic, bootstrap_servers="%s:%d" % (host, port))

        MQListener.__init__(self)
        LoggableMixin.__init__(self, KafkaListener)

    def _listen(self):
        self.logger.debug("Fetching messages")

        for msg in self.consumer:
            self.q.put(msg)

    def _decode(self, raw_record):
        record = ListenerRecord()
        record.key = raw_record.key.decode("utf8")
        record.value = raw_record.value.decode("utf8")

        return record
