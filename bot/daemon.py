import time

from bot.util.asserting import TypeChecker

from bot.strategy.pipeline.block import Block
from util.logging import LoggableMixin


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

            for i in range(len(self.blocks)):
                b = self.blocks[i]
                self.logger.info("Running block number %d" % i)
                b.run()

            self.logger.debug("Waiting %f seconds" % self.dt_seconds)
            self.logger.debug("")
            time.sleep(self.dt_seconds)
