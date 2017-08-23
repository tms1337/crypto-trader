from kafka import KafkaProducer

from service.mq.mqwriter import MQWriter
from util.asserting import TypeChecker


class KafkaWriter(MQWriter):
    def __init__(self,
                 topic,
                 host="localhost",
                 port=9092):
        TypeChecker.check_type(topic, str)
        TypeChecker.check_type(host, str)
        TypeChecker.check_type(port, int)

        self.topic = topic
        self.producer = KafkaProducer(bootstrap_servers="%s:%d" % (host, port),
                                      key_serializer=str.encode,
                                      value_serializer=str.encode)

    def write(self, key, value):
        super(KafkaWriter, self).write(key, value)
        self.producer.send(self.topic, key=key, value=value)