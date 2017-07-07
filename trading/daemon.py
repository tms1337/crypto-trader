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

                partial_decision = self.trade_decider.decide()
                full_decision = self.volume_decider.decide(partial_decision)

                if self.verbose >= 2:
                    print("Decision made\n %s" % str(full_decision))

                self.apply_decision(full_decision)
            except Exception as ex:
                print("An error has occured %s" % str(ex))
            else:
                self.trade_decider.apply_last()

            time.sleep(self.dt_seconds)

    def apply_decision(self, decision):
        if self.verbose >= 1:
            print("Making trade offer")
        pass
