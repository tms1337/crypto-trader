from bot.strategy.pipeline.monitoring.monitor import MonitorMixin
from util.asserting import TypeChecker


class MonitoredMixin:
    def __init__(self, monitors=None):
        if monitors is None:
            monitors = []

        TypeChecker.check_type(monitors, list)
        for observer in monitors:
            TypeChecker.check_type(observer, MonitorMixin)

        self.monitors = monitors

    def notify(self, data):
        for monitor in self.monitors:
            monitor.notify(data)