import datetime
import time

from trading.deciders.transaction.base import TransactionDecider
from trading.deciders.volume.base import VolumeDecider


class Daemon:
    def __init__(self,
                 trader,
                 transaction_decider,
                 volume_decider,
                 dt_seconds=60,
                 verbose=1):

        self._check_trader(trader)
        self._check_transaction_decider(transaction_decider)
        self._check_volume_decider(volume_decider)
        self._check_dt_seconds(dt_seconds)

        self.trader = trader
        self.transaction_decider = transaction_decider
        self.volume_decider = volume_decider
        self.dt_seconds = dt_seconds
        self.verbose = verbose

    def run(self):
        while True:
            if self.verbose >= 1:
                print("Time: %s" % (datetime.datetime.now()))
            try:
                if self.verbose >= 1:
                    print("Making decision")

                partial_decisions = self.transaction_decider.decide()
                full_decisions = self.volume_decider.decide(partial_decisions)

                if self.verbose >= 2:
                    print("Decision made\n\t%s" % str(full_decisions))

                for decision in full_decisions:
                    decision.check_validity()

                self.apply_decisions(full_decisions)
            except Exception as ex:
                print("\033[91mAn error has occurred while creating decision, waiting for the next step"
                      "\n\tError: %s\033[0m" % str(ex))
            else:
                try:
                    self.transaction_decider.apply_last()
                except Exception as ex_inner:
                    print("\033[91mAn error has occurred while applying decision, waiting for the next step"
                          "\n\tError: %s\033[0m" % str(ex_inner))

            if self.verbose >= 1:
                print("\n")
                for _ in range(100):
                    print("-", end="")
                print("\n")

            time.sleep(self.dt_seconds)

    def apply_decisions(self, decisions):
        if self.verbose >= 1:
            print("Applying decision %s" % str(decisions))

        failed_decisions = self.trader.create_bulk_offers(decisions)
        if len(failed_decisions) != 0:
            raise RuntimeError("An error has occured during transaction execution, "
                               "\n\tFailed decisions %s" % str(failed_decisions))

        self.transaction_decider.apply_last()

        if self.verbose >= 1:
            print("\033[92mDecision succesfully applied"
                  "\n\tTotal balance: %s\033[0m" % (self.trader.total_balance()))

    @staticmethod
    def _check_trader(trader):
        # TODO: check real class
        pass

    @staticmethod
    def _check_transaction_decider(transaction_decider):
        if not isinstance(transaction_decider, TransactionDecider):
            raise ValueError("Transaction decider must be instance of TransactionDecider")

    @staticmethod
    def _check_volume_decider(volume_decider):
        if not isinstance(volume_decider, VolumeDecider):
            raise ValueError("Volume decider must be instance of VolumeDecider")

    @staticmethod
    def _check_dt_seconds(dt_seconds):
        if dt_seconds < 1:
            raise ValueError("dt must be larger or equal to 1")
