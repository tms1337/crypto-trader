from abc import ABC, abstractclassmethod
from queue import Queue
from threading import Thread

import time

from util.asserting import TypeChecker
from util.logging import LoggableMixin

class ListenerRecord:
    key = None
    value = None

class MQListener(ABC, LoggableMixin):
    def __init__(self, pause_dt):
        TypeChecker.check_one_of_types(pause_dt, [float, int])
        assert pause_dt > 0, \
            "Pause %f must be greatere than 0" % pause_dt

        self.pause_dt = pause_dt
        self.q = Queue()

        self.stop = False
        self.pause = False

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

    def pause(self):
        self.pause = True

    def resume(self):
        self.pause = False

    def stop(self):
        self.stop = True

    def _listen(self):
        while True:
            if not self.pause:
                self._listen_once()

            if self.stop:
                break

            self.logger.debug("Sleeping")
            time.sleep(self.pause_dt)

    @abstractclassmethod
    def _listen_once(self):
        pass

    @abstractclassmethod
    def _decode(self, value):
        pass
