from unittest import TestCase
from .statsprovider import StatsProvider


class TestStatsProvider(TestCase):

    def test_main(self):
        stats = StatsProvider()
        history = stats.spread_history()
        avg_price = stats.average_price()

        pass

