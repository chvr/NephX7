import logging
#from chyros import loggingutil
#from samplemodules.module01 import Module01
from Scripts.chyros.template.chyros import loggingutil
from Scripts.chyros.template.samplemodules.module01 import Module01

__author__ = 'ChyrosNX'


def main():
    loggingutil.create('main.log')
    logging.info('Hello World!')

    m = Module01()

main()
