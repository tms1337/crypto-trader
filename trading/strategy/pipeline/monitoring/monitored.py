from trading.strategy.pipeline.monitoring.monitor import MonitorMixin
from trading.util.asserting import TypeChecker


class MonitoredMixin:
    def __init__(self, observers=None):
        if observers is None:
            observers = []

        TypeChecker.check_type(observers, list)
        for observer in observers:
            TypeChecker.check_type(observer, MonitorMixin)

        self.observers = observers

    def notify(self, data):
        for observer in self.observers:
            observer.notify(data)