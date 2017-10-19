from util.asserting import TypeChecker
from retrying import retry

from bot.exceptions.servererror import ServerError
from bot.exceptions.transactionnotexecuted import TransactionNotExecutedError
from bot.exceptions.util import is_provider_error
from bot.exchange.base import TradeProvider
from bot.strategy.decision import ExecutedDecision
from bot.strategy.transaction import Transaction
from util.logging import LoggableMixin

transactionexecutor_max_retry_attempts = None


class TransactionExecutor(LoggableMixin):
    def __init__(self,
                 trade_providers,
                 retry_attempts=3):

        TypeChecker.check_type(trade_providers, dict)
        for t in trade_providers:
            TypeChecker.check_type(t, str)
            TypeChecker.check_type(trade_providers[t], TradeProvider)

        self.trade_providers = trade_providers

        # hacky contd. :D
        global transactionexecutor_max_retry_attempts
        transactionexecutor_max_retry_attempts = retry_attempts

        LoggableMixin.__init__(self, TransactionExecutor)

    def execute_batch(self, transactions):
        failed_transactions = []

        TypeChecker.check_type(transactions, list)
        for t in transactions:
            TypeChecker.check_type(t, Transaction)

        for t in transactions:
            try:
                self.execute(t)
                for d in t.decisions:
                    assert not d is None, "Decision %s should have decider" % d
                    d.decider.apply_last()
            except TransactionNotExecutedError:
                failed_transactions.append(t)

        return failed_transactions

    def execute(self, transaction):
        TypeChecker.check_type(transaction, Transaction)

        executed_decisions = []
        for decision in transaction.decisions:
            exchange = decision.exchange
            if not exchange in self.trade_providers:
                raise ValueError("Exchange %s not in list" % exchange)

            try:
                executed_decisions.append(self._execute_single_decision(decision))
            except (ConnectionError, ServerError):
                self._revert(executed_decisions)
                raise TransactionNotExecutedError()

    # @retry(retry_on_exception=is_provider_error,
    #        stop_max_attempt_number=transactionexecutor_max_retry_attempts)
    def _execute_single_decision(self, decision):
        self.logger.debug("Executing decision %s" % decision)
        exchange = decision.exchange

        trader = self.trade_providers[exchange]
        id = trader.execute_single_decision(decision)

        executed = ExecutedDecision()
        executed.id = id
        executed.exchange = exchange

        return executed

    def _revert(self, executed_decisions):
        self.logger.debug("Decision failed, reverting transaction")
        for d in executed_decisions:
            self.logger.debug("Reverting decision %s" % d)
            trader = self.trade_providers[d.exchange]
            trader.cancel_offer(d.id)
