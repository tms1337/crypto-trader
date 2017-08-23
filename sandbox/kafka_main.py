import time

from service.mq.kafka.kafkalistener import KafkaListener
from service.mq.kafka.kafkawriter import KafkaWriter

listener = KafkaListener(topic="test", pause_dt=10)
listener.start()

writer = KafkaWriter(topic="test")

while True:
    writer.write("hamo", "karinada")
    print(listener.next())
    time.sleep(5)