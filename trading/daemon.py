import time


class Daemon:
    def __init__(self, trader, trade_decider, volume_decider, dt=60):
        self.trader = trader
        self.trade_decider = trade_decider
        self.volume_decider = volume_decider
        self.dt = dt

    def start(self):
        while True:
            time.sleep(self.dt)
