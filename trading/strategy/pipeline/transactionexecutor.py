from retrying import retry

from trading.exceptions.servererror import ServerError
from trading.exceptions.transactionnotexecuted import TransactionNotExecutedError
from trading.exceptions.util import is_provider_error
from trading.exchange.base import TradeProvider
from trading.strategy.decision import ExecutedDecision
from trading.strategy.pipeline.transaction import Transaction
from trading.util.typechecker import TypeChecker

# hacky
max_retry_attempts = None

class TransactionExecutor:
    def __init__(self,
                 trade_providers,
                 retry_attempts=3):

        TypeChecker.check_type(trade_providers, list)
        for t in trade_providers:
            TypeChecker.check_type(t, str)
            TypeChecker.check_type(trade_providers[t], TradeProvider)

        self.trade_providers = trade_providers

        # hacky contd. :D
        global max_retry_attempts
        max_retry_attempts = retry_attempts

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

    @retry(retry_on_exception=is_provider_error,
           stop_max_attempt_numer=max_retry_attempts)
    def _execute_single_decision(self, decision):
        exchange = decision.exchange

        trader = self.trade_providers[exchange]
        id = trader.execute_single_decision(decision)

        executed = ExecutedDecision()
        executed.id = id
        executed.exchange = exchange

        return executed

    def _revert(self, executed_decisions):
        for d in executed_decisions:
            trader = self.trade_providers[d.exchange]
            trader.cancel_offer(d.id)
