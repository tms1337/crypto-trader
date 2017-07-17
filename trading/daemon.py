import datetime
import logging
import random
import time

from trading.deciders.transaction.base import TransactionDecider
from trading.deciders.volume.base import VolumeDecider
from trading.exchange.base import ExchangeWrapper, ExchangeWrapperContainer


class Daemon:
    def __init__(self,
                 wrapper_container,
                 transaction_deciders,
                 volume_decider,
                 dt_seconds=60,
                 dt_timeout_seconds=3,
                 logger_name="app"):

        self._check_wrapper_container(wrapper_container)
        self._check_transaction_deciders(transaction_deciders)
        self._check_volume_decider(volume_decider)
        self._check_dt_seconds(dt_seconds)

        self.wrapper_container = wrapper_container
        self.transaction_deciders = transaction_deciders
        self.volume_decider = volume_decider
        self.dt_seconds = dt_seconds
        self.dt_timeout_seconds = dt_timeout_seconds

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.Daemon" % logger_name)

    def run(self):
        exception_n = 0

        while True:
            try:
                self.logger.info("Making decision")

                partial_decisions = []
                for transaction_decider in self.transaction_deciders:
                    partial_decisions = transaction_decider.decide(partial_decisions)
                    time.sleep(self.dt_timeout_seconds)

                full_decisions = self.volume_decider.decide(partial_decisions)

                self.logger.info("Decision made:\n%s" % str(full_decisions))

                for decision in full_decisions:
                    if isinstance(decision, tuple):
                        for d in decision:
                            d.check_validity()
                    else:
                        decision.check_validity()

                # so exchange does not time us out
                time.sleep(self.dt_timeout_seconds)

                self.apply_decisions(full_decisions)
            except Exception as ex:
                exception_n += 1

                if exception_n >= 5:
                    exit(1)

                error_message = "An error has occurred while creating decision, waiting for the next step"
                self.logger.error(error_message)
            else:
                try:
                    for transaction_decider in self.transaction_deciders:
                        transaction_decider.apply_last()

                except Exception as ex_inner:
                    print("\033[91mAn error has occurred while applying decision, waiting for the next step"
                          "\n\tError: %s\033[0m" % str(ex_inner))


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

        self.logger.info("Total balance:\n\n")
        self.wrapper_container.print_balance()

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
