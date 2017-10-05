from tensorforce.agents import Agent

from bot.strategy.deciders.decider import Decider
from util.asserting import TypeChecker


class RLJianh17Decide(Decider):
    def __init__(self, agent, **kwargs):
        TypeChecker.check_one_of_types(agent, Agent)
        self.agent = agent

        Decider.__init__(**kwargs)

    def decide(self, informer, historic_data=None):
        super().decide(informer, historic_data)

        self._normalize_historic_data(historic_data)


        print('before act')

        action = self.agent.act(historic_data, deterministic=True)

        print(action)

        input('stop.')

        return [], {}

    def _normalize_historic_data(self, historic_data):
        for i in range(historic_data.shape[0]):
            historic_data[i] /= historic_data[i, -1, 0]

    def apply_last(self):
        super().apply_last()
