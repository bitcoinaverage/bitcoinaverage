#!/usr/bin/python2.7
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))


import json
import requests
import time
from decimal import Decimal

from bitcoinaverage.config import EXCHANGE_LIST, CURRENCY_LIST, DEC_PLACES, API_QUERY_FREQUENCY, COUCHDB
from bitcoinaverage import api_parsers

start = time.time()

while True:

    all_rates = []

    for exchange_name in EXCHANGE_LIST:
        result = getattr(api_parsers, exchange_name+'ApiCall')(**EXCHANGE_LIST[exchange_name])
        print ' '
        print exchange_name
        print time.time() - start
        print ' '
        all_rates.append(result)

    last_average_rates = requests.get(url=COUCHDB['RATES_URL']).json()

    for currency in CURRENCY_LIST:
        last_average_rates[currency] = {'value': Decimal(0.00),
                                        'count': 0,
                                        }

    for rate in all_rates:
        for currency in CURRENCY_LIST:
            if currency in rate:
                last_average_rates[currency]['value'] = ( ( (last_average_rates[currency]['value']*Decimal(last_average_rates[currency]['count']))
                                                            + rate[currency]['last'])
                                                         / Decimal(last_average_rates[currency]['count']+1) )
                last_average_rates[currency]['count'] = last_average_rates[currency]['count'] + 1

                last_average_rates[currency]['value'] = last_average_rates[currency]['value'].quantize(DEC_PLACES)


    for currency in CURRENCY_LIST:
        last_average_rates[currency]['value'] = str(last_average_rates[currency]['value'])
        last_average_rates[currency]['count'] = str(last_average_rates[currency]['count'])

    response = requests.put(url=COUCHDB['RATES_URL'], data=json.dumps(last_average_rates))

    time.sleep(API_QUERY_FREQUENCY)
