from abc import ABC

from bot.strategy.pipeline.informer import Informer
from bot.strategy.pipeline.monitoring.monitor import MonitorMixin
from util.asserting import TypeChecker


class InfoMonitor(MonitorMixin, ABC):
    def check_data(self, data):
        TypeChecker.check_type(data, Informer)
