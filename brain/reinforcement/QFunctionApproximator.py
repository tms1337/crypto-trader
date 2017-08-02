from abc import ABC, abstractclassmethod

from brain.reinforcement.statevector import StateVector
from util.asserting import TypeChecker


class QFunctionApproximator(ABC):
    def __init__(self, dimension_n):
        TypeChecker.check_type(dimension_n, int)
        assert dimension_n > 0, "Dimension must be greater than 0"

        self.dimension_n = dimension_n

    def get_dimension_n(self):
        return self.dimension_n

    @abstractclassmethod
    def choose_next_action(self, state):
        self._check_state(state)

    @abstractclassmethod
    def update_q_value(self, state, action, next_state, reward):
        self._check_state(state)
        self._check_state(next_state)

        TypeChecker.check_one_of_types(reward, [float, int])

    def _check_state(self, state):
        TypeChecker.check_type(state, StateVector)
        assert state.get_dimension_n == self.dimension_n, \
            "You must provide the state with %d dimensions" % self.dimension_n
