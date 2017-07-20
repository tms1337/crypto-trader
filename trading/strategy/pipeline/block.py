from trading.strategy.pipeline.deciderpipeline import DeciderPipeline
from trading.strategy.pipeline.informer import Informer
from trading.strategy.pipeline.transactionexecutor import TransactionExecutor
from trading.util.typechecker import TypeChecker


class Block:
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

    def run(self):
        stats_matrix = self.informer.stats_matrix()
        transactions = self.decider_pipeline.decide(stats_matrix)
        failed_transactions = self.transaction_executor.execute_batch(transactions)