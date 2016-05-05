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
    runner.set_args({'rpcport': '--rpcport "8002"'})
    runner.create_accts(4)
    runner.ext_accts(['43f41cdca2f6785642928bcd2265fe9aff02911a'])
    runner.run()
    if sys.version_info >= (3, 0):
        input("Press Enter to Stop process")
    else:
        raw_input("Press Enter to Stop process")
    runner.stop(cleanup=False)


    
