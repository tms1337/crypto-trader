from service.mq.mqlistener import MQListener, ListenerRecord
from kafka import KafkaConsumer

from util.asserting import TypeChecker


class KafkaListener(MQListener):
    def __init__(self,
                 topic,
                 host="localhost",
                 port=9092,
                 pause_dt=1):
        TypeChecker.check_type(topic, str)
        TypeChecker.check_type(host, str)
        TypeChecker.check_type(port, int)

        TypeChecker.check_one_of_types(pause_dt, [int, float])
        assert pause_dt > 0, \
            "Pause %f must be greater than 0" % pause_dt

        self.consumer = KafkaConsumer(topic, bootstrap_servers="%s:%d" % (host, port))

        MQListener.__init__(self, pause_dt)

    def _listen_once(self):
        for msg in self.consumer:
            self.q.put(msg)

    def _decode(self, raw_record):
        record = ListenerRecord()
        record.key = raw_record.key
        record.value = raw_record.value

        return record
