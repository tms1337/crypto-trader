from abc import ABC, abstractclassmethod
from enum import unique, Enum
from queue import Queue
from threading import Thread

from util.asserting import TypeChecker
from util.logging import LoggableMixin


@unique
class BotActionType(Enum):
    CHANGE_PARAMETERS = 1
    PAUSE = 2
    RESUME = 3
    STOP = 4


class BotAction:
    def __init__(self, action_type, parameters=None):
        TypeChecker.check_type(action_type, BotActionType)
        if not parameters is None:
            TypeChecker.check_type(parameters, dict)

        self.action_type = action_type
        self.parameters = parameters


class BotType(ABC, LoggableMixin):
    def __init__(self, parameters):
        self.q = Queue()
        self.pause = False
        self.stop = False

        TypeChecker.check_type(parameters, dict)
        self.parameters = parameters

        LoggableMixin.__init__(self, BotType)

    @staticmethod
    def name():
        # hacky :(((
        # enforce children to implement this static method
        raise NotImplementedError("You should implement static name method")

    @staticmethod
    def list_parameters():
        raise NotImplementedError("You should implement static name method")

    @abstractclassmethod
    def run_step(self):
        pass

    @abstractclassmethod
    def get_parameters(self):
        pass

    @abstractclassmethod
    def change_parameters(self, parameters):
        pass

    def check_q(self):
        if not self.q.empty():
            action = self.q.get()

            if action.action_type == BotActionType.CHANGE_PARAMETERS:
                self.change_parameters(action.parameters)
            elif action.action_type == BotActionType.PAUSE:
                self.pause = True
            elif action.action_type == BotActionType.RESUME:
                self.pause = False
            elif action.action_type == BotActionType.STOP:
                self.stop = True

            self.q.task_done()

    def run(self):
        while True:
            self.check_q()

            if not self.pause:
                self.logger.info("Executing step")
                self.run_step()

            if self.stop:
                self.logger.info("Stopping")
                break

    def spawn(self):
        t = Thread(target=self.run)
        t.start()

    def enqueue_action(self, action):
        TypeChecker.check_type(action, BotAction)
        self.q.put(action)
