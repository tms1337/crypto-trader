import time


class Daemon:

    def __init__(self,
                 trader,
                 trade_decider,
                 volume_decider,
                 dt_seconds=60,
                 verbose=1):

        self.trader = trader
        self.trade_decider = trade_decider
        self.volume_decider = volume_decider
        self.dt_seconds = dt_seconds
        self.verbose = verbose

    def run(self):
        while True:
            try:
                if self.verbose >= 1:
                    print("Making decision")

                partial_decisions = self.trade_decider.decide()
                full_decisions = self.volume_decider.decide(partial_decisions)

                if self.verbose >= 2:
                    print("Decision made\n %s" % str(full_decisions))

                for decision in full_decisions:
                    decision.check_validity()

                self.apply_decisions(full_decisions)
            except Exception as ex:
                print("033[91mAn error has occured, proceeding with next step"
                      "\n\tError: %s\033[0m" % str(ex))
            else:
                self.trade_decider.apply_last()

            time.sleep(self.dt_seconds)

    def apply_decisions(self, decisions):
        if self.verbose >= 1:
            print("Applying decision %s" % str(decisions))

        self.trader.create_bulk_offers(decisions)
        self.trade_decider.apply_last()

        if self.verbose >= 1:
            print("'\033[92mDecision succesfully applied\033[0m")
