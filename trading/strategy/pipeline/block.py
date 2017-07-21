from trading.strategy.pipeline.deciderpipeline import DeciderPipeline
from trading.strategy.pipeline.informer import Informer
from trading.strategy.pipeline.transactionexecutor import TransactionExecutor
from trading.util.asserting import TypeChecker

from trading.util.logging import LoggableMixin


class Block(LoggableMixin):
    def __init__(self,
                 informer,
                 decider_pipeline,
                 transaction_executor):
        TypeChecker.check_type(informer, Informer)
        TypeChecker.check_type(decider_pipeline, DeciderPipeline)
        TypeChecker.check_type(transaction_executor, TransactionExecutor)

        self.informer = informer
        self.decider_pipeline = decider_pipeline
        self.transaction_executor = transaction_executor

        LoggableMixin.__init__(self, Block)

    def run(self):
        self.logger.debug("Starting information retrieval")
        stats_matrix = self.informer.get_stats_matrix()
        try:
            self.logger.debug("Starting decision pipeline")
            transactions = self.decider_pipeline.decide(stats_matrix)
            self.logger.debug("Decided transactions %s" % transactions)
        except AssertionError as error:
            self.logger.error("Assertion error while executing transaction: %s" % error)
        else:
            failed_transactions = self.transaction_executor.execute_batch(transactions)
            self.logger.warn("Failed transactions %s" % failed_transactions)
