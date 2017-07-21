import time

from trading.strategy.pipeline.block import Block
from trading.util.asserting import TypeChecker
from trading.util.logging import LoggableMixin


class Daemon(LoggableMixin):
    def __init__(self,
                 blocks,
                 dt_seconds=60):

        TypeChecker.check_type(blocks, list)
        for b in blocks:
            TypeChecker.check_type(b, Block)

        self.blocks = blocks

        TypeChecker.check_one_of_types(dt_seconds, [float, int])
        self.dt_seconds = dt_seconds

        LoggableMixin.__init__(self, Daemon)

    def run(self):
        while True:
            self.logger.debug("Starting step")
            for b in self.blocks:
                self.logger.debug("Running block %s" % b)
                b.run()

            self.logger.debug("Waiting %f seconds" % self.dt_seconds)
            time.sleep(self.dt_seconds)
