import datetime
import logging
import random
import time

from trading.strategy.transaction.base import TransactionDecider
from trading.strategy.volume.base import VolumeDecider
from trading.exchange.base import ExchangeWrapper, ExchangeWrapperContainer


class Daemon:
    def __init__(self,
                 wrapper_container,
                 transaction_deciders,
                 volume_deciders,
                 dt_seconds=60,
                 dt_timeout_seconds=0.5,
                 logger_name="app"):

        self._check_wrapper_container(wrapper_container)
        self._check_transaction_deciders(transaction_deciders)
        self._check_volume_deciders(volume_deciders)
        self._check_dt_seconds(dt_seconds)

        self.wrapper_container = wrapper_container
        self.transaction_deciders = transaction_deciders
        self.volume_deciders = volume_deciders
        self.dt_seconds = dt_seconds
        self.initial_dt_seconds = dt_seconds
        self.dt_timeout_seconds = dt_timeout_seconds

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.Daemon" % logger_name)

        self.total_transactions = 0

    def run(self):
        exception_n = 0

        while True:
            try:
                self.wrapper_container.print_balance()

                self.logger.info("Making decision")

                decisions = []
                for i in range(len(self.transaction_deciders)):
                    transaction_decider = self.transaction_deciders[i]
                    volume_decider = self.volume_deciders[i]

                    decisions = transaction_decider.decide(decisions)
                    decisions = volume_decider.decide(decisions)

                self.logger.info("Decisions made:\n%s" % str(decisions))

                for decision in decisions:
                    if isinstance(decision, tuple):
                        for d in decision:
                            d.check_validity()
                    else:
                        decision.check_validity()

                # so exchange does not time us out
                self.apply_decisions(decisions)
            except Exception as ex:
                exception_n += 1

                if exception_n >= 3:
                    self.dt_seconds *= 1.5
                    exception_n = 0
                    self.logger.info("Increasing waiting time to %f to prevent further errors" % self.dt_seconds)

                error_message = "An error has occurred while creating or applying decision, waiting for the next step\nError: %s" % ex
                self.logger.error(error_message)
            else:
                # try:
                #     for transaction_decider in self.transaction_deciders:
                #         transaction_decider.apply_last()
                #
                # except Exception as ex_inner:
                #     print("An error has occurred while applying decision, waiting for the next step"
                #           "\n\tError: %s" % str(ex_inner))

                if self.dt_seconds > self.initial_dt_seconds:
                    self.dt_seconds /= 1.5

            time.sleep(random.uniform(0.8 * self.dt_seconds, self.dt_seconds))

    def apply_decisions(self, decisions):
        self.logger.info("Applying decision\n%s" % str(decisions))

        failed_decisions = self.wrapper_container.create_bulk_offers(decisions)
        if failed_decisions is not None and len(failed_decisions) != 0:
            error_message = "An error has occured during transaction execution, " \
                            "\n\tFailed decisions %s" % str(failed_decisions)

            self.logger.error(error_message)
            raise RuntimeError(error_message)

        self.logger.info("Decision succesfully applied")
        self.total_transactions += 1

        if self.total_transactions % 10 == 1:
            f = open('./total_transactions', 'a+')
            f.write(str(self.total_transactions))
            f.close()

    def _check_wrapper_container(self, wrapper_container):
        if not isinstance(wrapper_container, ExchangeWrapperContainer):
            error_message = "Wrapper container decider must be an instance of ExchangeWrapperContainer"

            self.logger.error(error_message)
            raise ValueError(error_message)

    def _check_transaction_decider(self, transaction_decider):
        if not isinstance(transaction_decider, TransactionDecider):
            error_message = "Transaction decider must be an instance of TransactionDecider"

            self.logger.error(error_message)
            raise ValueError(error_message)

    def _check_volume_deciders(self, volume_deciders):
        for decider in volume_deciders:
            self._check_volume_decider(decider)

    def _check_volume_decider(self, volume_decider):
        if not isinstance(volume_decider, VolumeDecider):
            error_message = "Volume decider must be an instance of VolumeDecider"

            self.logger.error(error_message)
            raise ValueError(error_message)

    def _check_dt_seconds(self, dt_seconds):
        if dt_seconds < 1:
            error_message = "dt must be larger or equal to 1"

            self.logger.error(error_message)
            raise ValueError(error_message)

    def _check_transaction_deciders(self, transaction_deciders):
        for transaction_decider in transaction_deciders:
            self._check_transaction_decider(transaction_decider)
