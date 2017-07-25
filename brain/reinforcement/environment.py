from abc import ABC, abstractclassmethod

from bot.util.asserting import TypeChecker
from brain.reinforcement.statevector import StateVector


class Environment(ABC):
    def __init__(self, initial_state):
        TypeChecker.check_type(initial_state, StateVector)
        self.state = initial_state

    @abstractclassmethod
    def next(self, action):
        pass

    def get_state(self):
        return self.state
