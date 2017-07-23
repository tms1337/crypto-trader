from trading.strategy.pipeline.informer import Informer
from trading.strategy.pipeline.monitoring.monitor import MonitorMixin
from trading.util.asserting import TypeChecker


class InfoMonitor(MonitorMixin):
    def check_data(self, data):
        TypeChecker.check_type(data, Informer)