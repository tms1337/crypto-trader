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
        try:
            self.logger.info("Starting decision pipeline")
            transactions = self.decider_pipeline.decide(self.informer)
            self.logger.debug("Decided transactions %s" % transactions)
        except AssertionError as error:
            self.logger.error("Assertion error while executing transaction: %s" % error)
        else:
            self.logger.debug("Starting transactions executions")
            failed_transactions = self.transaction_executor.execute_batch(transactions)

            if len(failed_transactions) != 0:
                self.logger.warn("Failed transactions %s" % failed_transactions)
            else:
                self.logger.info("All transactions successful")

                # TODO: refactor into monitors
                total_balance = {}

                balances_matrix = self.informer.get_balances_matrix()
                for e in balances_matrix.all_exchanges():
                    for c in balances_matrix.all_currencies():
                        if c not in total_balance:
                            total_balance[c] = 0

                        total_balance[c] += balances_matrix.get(e, c).value

                self.logger.debug(total_balance)