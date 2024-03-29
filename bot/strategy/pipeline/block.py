from util.asserting import TypeChecker

from bot.strategy.pipeline.deciderpipeline import DeciderPipeline
from bot.strategy.pipeline.informer import Informer
from bot.strategy.pipeline.monitoring.monitor import MonitorMixin
from bot.strategy.pipeline.monitoring.monitored import MonitoredMixin
from bot.strategy.pipeline.transactionexecutor import TransactionExecutor
from util.logging import LoggableMixin


class Block(LoggableMixin, MonitoredMixin):
    def __init__(self,
                 informer,
                 decider_pipeline,
                 transaction_executor,
                 monitors=None):
        TypeChecker.check_type(informer, Informer)
        self.informer = informer

        TypeChecker.check_type(decider_pipeline, DeciderPipeline)
        self.decider_pipeline = decider_pipeline

        TypeChecker.check_type(transaction_executor, TransactionExecutor)
        self.transaction_executor = transaction_executor

        if monitors is None:
            monitors = []
        TypeChecker.check_type(monitors, list)
        for m in monitors:
            TypeChecker.check_type(m, MonitorMixin)
        MonitoredMixin.__init__(self, monitors)

        LoggableMixin.__init__(self, Block)

    def run(self):
        self.logger.debug("Starting information retrieval")
        self.informer.set_all()

        try:
            self.logger.info("Starting decision pipeline")

            deciders_data = { 'informer': self.informer }
            deciders_data['transactions'], deciders_data['misc'] = self.decider_pipeline.decide(self.informer)

            self.logger.debug("Decided transactions %s" % deciders_data['transactions'])
        except AssertionError as error:
            self.logger.error("Assertion error while executing transaction: %s" % error)
        else:
            self.logger.debug("Starting transactions executions")
            failed_transactions = self.transaction_executor.execute_batch(deciders_data['transactions'])

            if len(failed_transactions) != 0:
                self.logger.warn("Failed transactions %s" % failed_transactions)
            else:
                self.logger.info("All transactions successful")

                self.logger.debug("Notifying monitors")
                self.notify(deciders_data)