from tensorforce.agents import Agent

from bot.strategy.deciders.decider import Decider
from util.asserting import TypeChecker


class RLJianh17Decide(Decider):
    def __init__(self, agent, init_data, **kwargs):
        TypeChecker.check_one_of_types(agent, Agent)
        self.agent = agent

        # TODO check if numpy array
        self.init_data = init_data

        Decider.__init__(**kwargs)

    def decide(self, informer, historic_data=None):
        super().decide(informer, historic_data)

        action = self.agent.act(historic_data, deterministic=True)

        print(action)

        return [], {}

    def apply_last(self):
        super().apply_last()
