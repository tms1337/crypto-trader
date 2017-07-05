from unittest import TestCase
from .stats import StatsProvider


class TestStatsProvider(TestCase):
    def test_construct(self):
        stats = StatsProvider()

    def test_construct_crypto_uppercase_random_string(self):
        with self.assertRaises(ValueError):
            stats = StatsProvider(crypto="ABC")

        with self.assertRaises(ValueError):
            stats = StatsProvider(crypto="XXX")

    def test_construct_crypto_lowercase_random_string(self):
        with self.assertRaises(ValueError):
            stats = StatsProvider(crypto="xxx")

    def test_construct_crypto_empty_string(self):
        with self.assertRaises(ValueError):
            stats = StatsProvider(crypto="")

    def test_construct_crypto_lowercase_valid(self):
        with self.assertRaises(ValueError):
            stats = StatsProvider(crypto="btc")

        with self.assertRaises(ValueError):
            stats = StatsProvider(crypto="eth")

    def test_construct_currency_uppercase_random_string(self):
        with self.assertRaises(ValueError):
            stats = StatsProvider(crypto="ABC")

        with self.assertRaises(ValueError):
            stats = StatsProvider(crypto="XXX")

    def test_construct_currency_lowercase_random_string(self):
        with self.assertRaises(ValueError):
            stats = StatsProvider(crypto="xxx")

    def test_construct_currency_empty_string(self):
        with self.assertRaises(ValueError):
            stats = StatsProvider(crypto="")

    def test_construct_currency_lowercase_valid(self):
        with self.assertRaises(ValueError):
            stats = StatsProvider(crypto="eur")

        with self.assertRaises(ValueError):
            stats = StatsProvider(crypto="usd")
