import logging

logger_name = "app"


def set_global_logger_name(next_logger_name):
    global logger_name
    logger_name = next_logger_name


class LoggableMixin:
    def __init__(self, called_from_class):
        assert not called_from_class is None, \
            "Called from class should not be none"

        global logger_name
        if not issubclass(type(self), called_from_class) or type(self) is called_from_class:
            self.logger = logging.getLogger("%s.%s" % (logger_name, self.__class__.__name__))
