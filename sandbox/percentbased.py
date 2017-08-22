from bot.exchange.kraken.stats import KrakenStatsProvider
from bot.exchange.kraken.trade import KrakenTradeProvider
from bot.exchange.poloniex.stats import PoloniexStatsProvider
from bot.exchange.poloniex.trade import PoloniexTradeProvider
from bot.strategy.deciders.simple.base import SimpleCompositeDecider
from bot.strategy.deciders.simple.offer.exchangediff import ExchangeDiffOfferDecider
from bot.strategy.deciders.simple.offer.percentbased import PercentBasedOfferDecider
from bot.strategy.deciders.simple.volume.fixedvalue import FixedValueVolumeDecider
from bot.strategy.pipeline.block import Block
from bot.strategy.pipeline.deciderpipeline import DeciderPipeline
from bot.strategy.pipeline.informer import Informer
from bot.strategy.pipeline.monitoring.mongobalancemonitor import MongoBalanceMonitor
from bot.strategy.pipeline.transactionexecutor import TransactionExecutor

from bot.daemon import Daemon
from bot.exchange.bitfinex.trade import BitfinexTradeProvider

from manager.bottype import BotType
from util.logging import LoggableMixin


class PercentBotType(BotType, LoggableMixin):
    def __init__(self, parameters):
        BotType.__init__(self, parameters)

        stats_providers = self.parameters["stats_providers"]
        trade_providers = self.parameters["trade_providers"]

        daemon_dt = self.parameters["daemon_dt"]
        currencies_for_crypto = self.parameters["currencies_for_crypto"]
        trading_currency_for_crypto = self.parameters["trading_currency_for_crypto"]
        crypto_values = self.parameters["crypto_values"]
        short_buy_threshold = self.parameters["short_buy_threshold"]
        short_sell_threshold = self.parameters["short_buy_threshold"]
        short_security_loss_threshold = self.parameters["short_security_loss_threshold"]
        long_buy_threshold = self.parameters["long_buy_threshold"]
        long_sell_threshold = self.parameters["long_sell_threshold"]
        long_security_loss_threshold = self.parameters["long_security_loss_threshold"]

        crypto_informer = Informer(base_currency=trading_currency_for_crypto,
                                   stats_providers=stats_providers,
                                   trade_providers=trade_providers,
                                   currencies=currencies_for_crypto)

        short_percent_crypto_decider = SimpleCompositeDecider(trade_providers=trade_providers,
                                                              offer_decider=PercentBasedOfferDecider(
                                                                  currencies=currencies_for_crypto,
                                                                  buy_threshold=short_buy_threshold,
                                                                  sell_threshold=short_sell_threshold,
                                                                  security_loss_threshold=short_security_loss_threshold,
                                                                  trading_currency=trading_currency_for_crypto),
                                                              volume_decider=FixedValueVolumeDecider(
                                                                  values=crypto_values))

        long_percent_crypto_decider = SimpleCompositeDecider(trade_providers=trade_providers,
                                                             offer_decider=PercentBasedOfferDecider(
                                                                 currencies=currencies_for_crypto,
                                                                 buy_threshold=long_buy_threshold,
                                                                 sell_threshold=long_sell_threshold,
                                                                 security_loss_threshold=long_security_loss_threshold,
                                                                 trading_currency=trading_currency_for_crypto),
                                                             volume_decider=FixedValueVolumeDecider(
                                                                 values=crypto_values))

        # he's gonna kill you !!!
        executor = TransactionExecutor(trade_providers=trade_providers)

        crypto_block = Block(decider_pipeline=DeciderPipeline(deciders=[short_percent_crypto_decider,
                                                                        long_percent_crypto_decider]),
                             informer=crypto_informer,
                             transaction_executor=executor)


        self.daemon = Daemon(blocks=[crypto_block],
                        dt_seconds=daemon_dt)

        LoggableMixin.__init__(self, PercentBotType)

    def change_parameters(self, parameters):
        pass

    @staticmethod
    def name():
        return "PercentBased"

    def get_parameters(self):
        pass

    def run_step(self):
        self.daemon.run()

