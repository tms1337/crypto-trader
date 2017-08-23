from abc import ABC, abstractclassmethod
from queue import Queue
from threading import Thread

from util.asserting import TypeChecker
from util.logging import LoggableMixin

class ListenerRecord:
    key = None
    value = None

class MQListener(ABC, LoggableMixin):
    def __init__(self):
        self.q = Queue()
        LoggableMixin.__init__(self, MQListener)

    def next(self):
        if self.q.empty():
            return None
        else:
            raw_record = self.q.get()
            self.q.task_done()

            record = self._decode(raw_record)
            TypeChecker.check_type(record, ListenerRecord)

            return record

    def start(self):
        t = Thread(target=self._listen)
        t.start()

    @abstractclassmethod
    def _listen(self):
        pass

    @abstractclassmethod
    def _decode(self, value):
        pass
