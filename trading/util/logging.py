import logging

logger_name = "app"


def set_global_logger_name(next_logger_name):
    global logger_name
    logger_name = next_logger_name


class LoggableMixin:
    def __init__(self):
        global logger_name
        self.logger = logging.getLogger("%s.%s" % (logger_name, self.__class__.__name__))
