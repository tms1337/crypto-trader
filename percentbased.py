from bot.exchange.bittrex.stats import BittrexStatsProvider
from bot.exchange.bittrex.trade import BittrexTradeProvider
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

        self.id = parameters["id"]
        del parameters["id"]

        providers_pause_dt = 0.15

        stats_providers = {
            # "poloniex": PoloniexStatsProvider(pause_dt=providers_pause_dt),
            "bittrex": BittrexStatsProvider(pause_dt=providers_pause_dt),
            # "bitfinex": BitfinexStatsProvider(),
            # "kraken": KrakenStatsProvider()
        }
        trade_providers = {
            # "poloniex": PoloniexTradeProvider(key_uri=("%s/poloniex" % keys_path), pause_dt=providers_pause_dt),
            "bittrex": BittrexTradeProvider(key_uri=("/home/ubuntu/production_keys/bittrex"), pause_dt=providers_pause_dt),
            # "bitfinex": BitfinexTradeProvider(key_uri=("%s/bitfinex" % keys_path)),
            # "kraken": KrakenTradeProvider(key_uri=("%s/kraken" % keys_path))
        }

        daemon_dt = self.parameters["daemon_dt"]
        currencies_for_crypto = self.parameters["currencies_for_crypto"]
        trading_currency_for_crypto = self.parameters["trading_currency_for_crypto"]
        crypto_values = self.parameters["crypto_values"]
        short_buy_threshold = self.parameters["short_buy_threshold"]
        short_sell_threshold = self.parameters["short_sell_threshold"]
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

    @staticmethod
    def list_parameters():
        parameter_objects = [
            {
                "name": "Bot pause",
                "alias": "daemon_dt",
                "description": "Period that the bot pauses between steps",
                "type": "number"
            },
            {
                "name": "Trading currencies",
                "alias": "currencies_for_crypto",
                "description": "Currencies that are traded by bot (comma separated!)",
                "type": "text"
            },
            {
                "name": "Base currency",
                "alias": "trading_currency_for_crypto",
                "description": "Currency that serves as a basis for trading",
                "type": "text"
            },
            {
                "name": "Amounts",
                "alias": "crypto_values",
                "description": "Amounts of each cryptocurrency to use in trading (JSON map)",
                "type": "text"
            },
            {
                "name": "Short buy threshold",
                "alias": "short_buy_threshold",
                "description": "Percent for the short bot to buy",
                "type": "number"
            },
            {
                "name": "Short sell threshold",
                "alias": "short_sell_threshold",
                "description": "Percent for the short bot to sell",
                "type": "number"
            },
            {
                "name": "Short security threshold",
                "alias": "short_security_loss_threshold",
                "description": "Percent for the short bot to sell to mitigate risk",
                "type": "number"
            },
            {
                "name": "Long buy threshold",
                "alias": "long_buy_threshold",
                "description": "Percent for the long bot to buy",
                "type": "number"
            },
            {
                "name": "Long sell threshold",
                "alias": "long_sell_threshold",
                "description": "Percent for the long bot to sell",
                "type": "number"
            },
            {
                "name": "Long security threshold",
                "alias": "long_security_loss_threshold",
                "description": "Percent for the long bot to sell to mitigate risk",
                "type": "number"
            },
            {
                "name": "Image url",
                "alias": "image_url",
                "description": "url of a bot image",
                "type": "text"
            }
        ]

        return parameter_objects

    def change_parameters(self, parameters):
        pass

    @staticmethod
    def name():
        return "PercentBased"

    def my_name(self):
        return self.name

    def get_parameters(self):
        return self.parameters

    def run_step(self):
        self.daemon.run()

    def get_info(self):
        status = {}
        self.logger.debug("Status %s" % self.pause)
        if self.pause:
            status["status"] = "paused"
        else:
            status["status"] = "active"
        status["name"] = self.parameters["name"]
        status["image_url"] = self.parameters["image_url"]
        parameter_objects = self.list_parameters()
        for p in parameter_objects:
            p["value"] = self.parameters[p["alias"]]
        status["parameters"] = parameter_objects
        status["id"] = self.id

        return status

