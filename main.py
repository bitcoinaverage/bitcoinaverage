#!/usr/bin/python2.7
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))


import json
import requests
from decimal import Decimal

from bitcoinaverage.config import EXCHANGE_LIST, CURRENCY_LIST, DEC_PLACES
from bitcoinaverage.config import COUCHDB
from bitcoinaverage import api_parsers



all_rates = []

for exchange_name in EXCHANGE_LIST:
    result = getattr(api_parsers, exchange_name+'ApiCall')(**EXCHANGE_LIST[exchange_name])
    all_rates.append(result)

last_average_rates = requests.get(url=COUCHDB['RATES_URL']).json()


for rate in all_rates:
    for currency in CURRENCY_LIST:
        if currency not in last_average_rates:
            last_average_rates[currency] = {'value': Decimal(0.00),
                                            'count': Decimal(0),
                                            }

        if currency in rate:
            last_average_rates[currency]['count'] = last_average_rates[currency]['count']+Decimal(1)
            last_average_rates[currency]['value'] = ( (last_average_rates[currency]['value']+rate[currency]['last'])
                                                     / last_average_rates[currency]['count'] )

            last_average_rates[currency]['value'] = last_average_rates[currency]['value'].quantize(DEC_PLACES)


for currency in CURRENCY_LIST:
    last_average_rates[currency]['value'] = str(last_average_rates[currency]['value'])
    last_average_rates[currency]['count'] = str(last_average_rates[currency]['count'])

# body = json.dumps({'test':'test'})
response = requests.put(url=COUCHDB['RATES_URL'], data=json.dumps(last_average_rates))
print response.json()
