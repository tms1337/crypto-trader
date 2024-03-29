from abc import ABC, abstractclassmethod

from brain.reinforcement.statevector import StateVector
from util.asserting import TypeChecker


class Environment(ABC):
    def __init__(self, initial_state):
        TypeChecker.check_type(initial_state, StateVector)
        self.state = initial_state

    @abstractclassmethod
    def next(self, action):
        pass

    def get_state(self):
        return self.state

    def get_dimension_n(self):
        return self.state.get_dimension_n()
