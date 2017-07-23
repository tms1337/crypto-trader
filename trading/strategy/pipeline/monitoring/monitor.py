from abc import abstractclassmethod, ABC


# noinspection PyAttributeOutsideInit
class MonitorMixin(ABC):
    def notify(self, monitored_data):
        self.check_data(monitored_data)
        self.monitored_data = monitored_data

    @abstractclassmethod
    def check_data(self, data):
        pass
