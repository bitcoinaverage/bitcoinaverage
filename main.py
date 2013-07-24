#!/usr/bin/python2.7
import os
import sys
from requests.exceptions import ConnectionError

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
        try:
            result = getattr(api_parsers, exchange_name+'ApiCall')(**EXCHANGE_LIST[exchange_name])
            result['exchange_name'] = exchange_name
            all_rates.append(result)
        except ConnectionError:
            pass

    previous_average_rates = requests.get(url=COUCHDB['TICKER_URL']).json()

    new_average_rates = {}
    if '_id' in previous_average_rates and '_rev' in previous_average_rates:
        new_average_rates['_id'] = previous_average_rates['_id']
        new_average_rates['_rev'] = previous_average_rates['_rev']

    total_volumes = {}
    relative_volumes = {}
    for currency in CURRENCY_LIST:
        new_average_rates[currency] = {'last': Decimal(0.00),
                                       'ask': Decimal(0.00),
                                       'bid': Decimal(0.00),
                                       'count': 0,
                                        }
        total_volumes[currency] = Decimal(0.00)
        relative_volumes[currency] = {}

    for rate in all_rates:
        for currency in CURRENCY_LIST:
            if currency in rate:
                total_volumes[currency] = total_volumes[currency] + rate[currency]['volume']

    for rate in all_rates:
        for currency in CURRENCY_LIST:
            if currency in rate:
                relative_volumes[currency][rate['exchange_name']] = rate[currency]['volume'] / total_volumes[currency]

    for rate in all_rates:
        for currency in CURRENCY_LIST:
            if currency in rate:
                new_average_rates[currency]['last'] = ( new_average_rates[currency]['last']
                                                        + rate[currency]['last'] * relative_volumes[currency][rate['exchange_name']] )
                new_average_rates[currency]['ask'] = ( new_average_rates[currency]['ask']
                                                        + rate[currency]['ask'] * relative_volumes[currency][rate['exchange_name']] )
                new_average_rates[currency]['bid'] = ( new_average_rates[currency]['bid']
                                                        + rate[currency]['bid'] * relative_volumes[currency][rate['exchange_name']] )


                # new_average_rates[currency]['ask'] = ( ( (new_average_rates[currency]['ask']*Decimal(new_average_rates[currency]['count']))
                #                                             + rate[currency]['ask'])
                #                                          / Decimal(new_average_rates[currency]['count']+1) )
                # new_average_rates[currency]['bid'] = ( ( (new_average_rates[currency]['bid']*Decimal(new_average_rates[currency]['count']))
                #                                             + rate[currency]['bid'])
                #                                          / Decimal(new_average_rates[currency]['count']+1) )
                # new_average_rates[currency]['count'] = new_average_rates[currency]['count'] + 1


                new_average_rates[currency]['last'] = new_average_rates[currency]['last'].quantize(DEC_PLACES)
                new_average_rates[currency]['ask'] = new_average_rates[currency]['ask'].quantize(DEC_PLACES)
                new_average_rates[currency]['bid'] = new_average_rates[currency]['bid'].quantize(DEC_PLACES)


    for currency in CURRENCY_LIST:
        new_average_rates[currency]['last'] = str(new_average_rates[currency]['last'])
        new_average_rates[currency]['ask'] = str(new_average_rates[currency]['ask'])
        new_average_rates[currency]['bid'] = str(new_average_rates[currency]['bid'])
        new_average_rates[currency]['count'] = str(new_average_rates[currency]['count'])

    response = requests.put(url=COUCHDB['TICKER_URL'], data=json.dumps(new_average_rates))

    time.sleep(API_QUERY_FREQUENCY)

{'USD': {'volume': Decimal('11629.64'), 'last': Decimal('94.69'), 'bid': Decimal('93.80'), 'high': Decimal('96.41'),
         'low': Decimal('92.30'), 'ask': Decimal('94.68')},
 'exchange_name': 'mtgox',
 'GBP': {'volume': Decimal('283.05'), 'last': Decimal('61.94'), 'bid': Decimal('60.07'), 'high': Decimal('64.20'),
         'low': Decimal('59.83'), 'ask': Decimal('62.12')},
 'RUR': {'volume': Decimal('2.57'), 'last': Decimal('3067.74'), 'bid': Decimal('2969.43'), 'high': Decimal('3159.41'),
         'low': Decimal('3053.17'), 'ask': Decimal('3104.98')},
 'EUR': {'volume': Decimal('1950.10'), 'last': Decimal('71.28'), 'bid': Decimal('71.28'), 'high': Decimal('74.50'),
         'low': Decimal('71.10'), 'ask': Decimal('71.70')},
 'CAD': {'volume': Decimal('150.84'), 'last': Decimal('97.66'), 'bid': Decimal('94.72'), 'high': Decimal('99.00'),
         'low': Decimal('96.07'), 'ask': Decimal('98.70')}}

