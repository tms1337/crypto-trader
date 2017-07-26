from brain.reinforcement import QFunctionApproximator
from brain.reinforcement.environment import Environment
from util.asserting import TypeChecker


class QLearner:
    def __init__(self,
                 approximator,
                 environment):

        TypeChecker.check_type(approximator, QFunctionApproximator)
        self.approximator = approximator

        TypeChecker.check_type(environment, Environment)
        self.environment = environment

    def train(self, step_n):
        TypeChecker.check_type(step_n, int)

        for _ in step_n:
            curr_state = self.environment.get_state()
            chosen_action = self.approximator.choose_next_action(curr_state)
            reward, next_state = self.environment.next(chosen_action)
            self.approximator.update(curr_state, chosen_action, next_state, reward)
