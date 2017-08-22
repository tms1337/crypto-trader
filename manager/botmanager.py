from manager.bottype import BotType, BotAction, BotActionType
from util.asserting import TypeChecker
from util.logging import LoggableMixin

import random


class BotManager(LoggableMixin):
    def __init__(self):
        self.types = {}
        self.bots = {}

        LoggableMixin.__init__(self, BotManager)

    def add_bot_type(self, bot_type):
        TypeChecker.check_type(bot_type, type)
        assert issubclass(bot_type, BotType)

        try:
            type_name = bot_type.name()

            if type_name in self.types:
                self.logger.warn("Trying to add already added type %s" % type_name)
            else:
                self.types[type_name] = bot_type
        except NotImplementedError:
            self.logger.error("Trying to add type that did not implement name method")

    def bot_types(self):
        return list(self.types.keys())

    def type_parameters(self, type_name):
        assert type_name in self.types, \
            "Type name %s must be in type list" % type_name

        return self.types[type_name]

    def spawn(self, type_name, parameters):
        assert type_name in self.types, \
            "Type name %s must be in type list" % type_name

        bot = self.types[type_name](parameters)

        hash = random.getrandbits(128)
        id = "%032x" % hash

        self.logger.debug("Starting bot %s" % id)

        self.bots[id] = bot

        bot.spawn()

        return id

    def pause(self, id):
        self._enqueue_no_parameter_action(id, BotActionType.PAUSE)

    def resume(self, id):
        self._enqueue_no_parameter_action(id, BotActionType.RESUME)

    def stop(self, id):
        self._enqueue_no_parameter_action(id, BotActionType.STOP)

    def _enqueue_no_parameter_action(self, id, action_type):
        TypeChecker.check_type(id, str)
        assert id in self.bots, \
            "Bot %s not in bot list" % id

        TypeChecker.check_type(action_type, BotActionType)

        self.logger.debug("Enqueing pause action for bot %s" % id)

        action = BotAction(action_type)
        self.bots[id].enqueue_action(action)
