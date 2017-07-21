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
        stats_matrix = self.informer.get_stats_matrix()
        try:
            transactions = self.decider_pipeline.decide(stats_matrix)
        except AssertionError as error:
            self.logger.error("Assertion error while executing transaction: %s" % error)
        else:
            failed_transactions = self.transaction_executor.execute_batch(transactions)
