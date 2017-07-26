from abc import ABC


class QFunctionApproximator(ABC):
    def choose_next_action(self, state):
        pass

    def update_q_value(self, state, action, next_state, reward):
        pass
