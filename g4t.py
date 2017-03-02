#
# Command-line driver
#
import sys
import logging
import time
from geth_for_test import GethRunner


def setup_logging():
    logging.basicConfig(level=logging.WARNING,
                        format=('%(levelname)s:'
                                    '%(name)s():'
                                    '%(funcName)s():'
                                    ' %(message)s')
                        )


if __name__ == '__main__':
    setup_logging()
    runner = GethRunner()
    runner.set_args({'rpcport': '--rpcport "8545"'})
    runner.create_accts(1)
    runner.ext_accts(['0xe51f7e720f4201f8bdd9a1bfd935f738bd028315',
                      '0x4871a4089f767f119c60b164388329fc2cdda32a',
                      '0x2e57890299979e6fbc7e2b001eefb9aab694e1f5',
                      '0x3546e826123a00782700e37c9fc921d18b82d79e',
                      '0x00788508461db89df194fa2f6d432a0f02d584b4',
                      '0xb2faa8ae4a3771a7485353d0fd46b24531edd818'
                      ])    
    
    runner.run()
    if sys.version_info >= (3, 0):
        input("Press Enter to Stop process")
    else:
        raw_input("Press Enter to Stop process")
    runner.stop(cleanup=False)


    
