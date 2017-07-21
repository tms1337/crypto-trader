from trading.strategy.pipeline.block import Block
from trading.util.asserting import TypeChecker


class Daemon:
    def __init__(self,
                 blocks,
                 dt_seconds=60):

        TypeChecker.check_type(blocks, list)
        for b in blocks:
            TypeChecker.check_type(b, Block)

        self.blocks = blocks

    def run(self):
        for b in self.blocks:
            b.run()
