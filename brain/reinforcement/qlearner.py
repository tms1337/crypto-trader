from brain.reinforcement import QFunctionApproximator
from brain.reinforcement.environment import Environment
from brain.reinforcement.statevector import StateVector
from util.asserting import TypeChecker


class QLearner:
    def __init__(self,
                 approximator,
                 environment):

        TypeChecker.check_type(approximator, QFunctionApproximator)
        self.approximator = approximator

        TypeChecker.check_type(environment, Environment)
        self.environment = environment

        assert approximator.get_dimension_n() == environment.get_dimension_n(), \
            "Approximator and environment need to have same dimensions"

    def train(self, step_n):
        TypeChecker.check_type(step_n, int)

        for _ in step_n:
            curr_state = self.environment.get_state()
            TypeChecker.check_type(curr_state, StateVector)

            chosen_action = self.approximator.choose_next_action(curr_state)

            reward, next_state = self.environment.next(chosen_action)
            TypeChecker.check_type(next_state, StateVector)
            TypeChecker.check_one_of_types(reward, [float, int])

            self.approximator.update(curr_state, chosen_action, next_state, reward)
