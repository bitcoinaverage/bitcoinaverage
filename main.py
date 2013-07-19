#!/usr/bin/python2.7
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from bitcoinaverage.config import EXCHANGE_LIST
from bitcoinaverage import api_parsers

rates = []

for exchange_name in EXCHANGE_LIST:
    result = getattr(api_parsers, exchange_name+'ApiCall')(**EXCHANGE_LIST[exchange_name])

    print ' '
    print exchange_name
    print 'last USD sell: '+str(result['USD']['last'])
    print 'all data:'
    print result
    print ' '




