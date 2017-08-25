from abc import ABC, abstractclassmethod
from multiprocessing import Queue
from threading import Thread

from multiprocessing import Process

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

            record = self._decode(raw_record)
            TypeChecker.check_type(record, ListenerRecord)

            return record

    def start(self):
        p = Process(target=self._listen)
        p.start()

    @abstractclassmethod
    def _listen(self):
        pass

    @abstractclassmethod
    def _decode(self, value):
        pass
