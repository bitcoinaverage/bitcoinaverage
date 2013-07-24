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
        all_rates.append(result)

    previous_average_rates = requests.get(url=COUCHDB['LAST_BID_ASK_URL']).json()

    new_average_rates = {'_id': previous_average_rates['_id'],
                         '_rev': previous_average_rates['_rev'],
                         }
    for currency in CURRENCY_LIST:
        new_average_rates[currency] = {'last': Decimal(0.00),
                                       'ask': Decimal(0.00),
                                       'bid': Decimal(0.00),
                                       'count': 0,
                                        }

    for rate in all_rates:
        for currency in CURRENCY_LIST:
            if currency in rate:
                new_average_rates[currency]['last'] = ( ( (new_average_rates[currency]['last']*Decimal(new_average_rates[currency]['count']))
                                                            + rate[currency]['last'])
                                                         / Decimal(new_average_rates[currency]['count']+1) )
                new_average_rates[currency]['ask'] = ( ( (new_average_rates[currency]['ask']*Decimal(new_average_rates[currency]['count']))
                                                            + rate[currency]['ask'])
                                                         / Decimal(new_average_rates[currency]['count']+1) )
                new_average_rates[currency]['bid'] = ( ( (new_average_rates[currency]['bid']*Decimal(new_average_rates[currency]['count']))
                                                            + rate[currency]['bid'])
                                                         / Decimal(new_average_rates[currency]['count']+1) )
                new_average_rates[currency]['count'] = new_average_rates[currency]['count'] + 1

                new_average_rates[currency]['last'] = new_average_rates[currency]['last'].quantize(DEC_PLACES)
                new_average_rates[currency]['ask'] = new_average_rates[currency]['ask'].quantize(DEC_PLACES)
                new_average_rates[currency]['bid'] = new_average_rates[currency]['bid'].quantize(DEC_PLACES)


    for currency in CURRENCY_LIST:
        new_average_rates[currency]['last'] = str(new_average_rates[currency]['last'])
        new_average_rates[currency]['ask'] = str(new_average_rates[currency]['ask'])
        new_average_rates[currency]['bid'] = str(new_average_rates[currency]['bid'])
        new_average_rates[currency]['count'] = str(new_average_rates[currency]['count'])

    response = requests.put(url=COUCHDB['LAST_BID_ASK_URL'], data=json.dumps(new_average_rates))

    time.sleep(API_QUERY_FREQUENCY)
