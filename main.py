#!/usr/bin/python2.7
import os
import sys
from requests.exceptions import ConnectionError
project_abs_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, project_abs_path)


import json
import time
from email import utils
from decimal import Decimal

from bitcoinaverage.config import EXCHANGE_LIST, CURRENCY_LIST, DEC_PLACES, API_QUERY_FREQUENCY, API_FILES
from bitcoinaverage import api_parsers


while True:

    exchanges_rates = []
    exchanges_ignored = []

    for exchange_name in EXCHANGE_LIST:
        try:
            result = getattr(api_parsers, exchange_name+'ApiCall')(**EXCHANGE_LIST[exchange_name])

            if result is not None:
                result['exchange_name'] = exchange_name
                exchanges_rates.append(result)
            else:
                exchanges_ignored.append(exchange_name)

        except (ValueError, ConnectionError):
            pass

    calculated_average_rates = {}
    total_volumes = {}
    calculated_relative_volumes = {}
    for currency in CURRENCY_LIST:
        calculated_average_rates[currency] = {'last': Decimal(0.00),
                                       'ask': Decimal(0.00),
                                       'bid': Decimal(0.00),
                                        }
        total_volumes[currency] = Decimal(0.00)
        calculated_relative_volumes[currency] = {}

    for rate in exchanges_rates:
        for currency in CURRENCY_LIST:
            if currency in rate:
                total_volumes[currency] = total_volumes[currency] + rate[currency]['volume']

    for rate in exchanges_rates:
        for currency in CURRENCY_LIST:
            if currency in rate:
                calculated_relative_volumes[currency][rate['exchange_name']] = rate[currency]['volume'] / total_volumes[currency]
                calculated_relative_volumes[currency][rate['exchange_name']] = calculated_relative_volumes[currency][rate['exchange_name']].quantize(Decimal('0.0000'))

    for rate in exchanges_rates:
        for currency in CURRENCY_LIST:
            if currency in rate:
                calculated_average_rates[currency]['last'] = ( calculated_average_rates[currency]['last']
                                                        + rate[currency]['last'] * calculated_relative_volumes[currency][rate['exchange_name']] )
                calculated_average_rates[currency]['ask'] = ( calculated_average_rates[currency]['ask']
                                                        + rate[currency]['ask'] * calculated_relative_volumes[currency][rate['exchange_name']] )
                calculated_average_rates[currency]['bid'] = ( calculated_average_rates[currency]['bid']
                                                        + rate[currency]['bid'] * calculated_relative_volumes[currency][rate['exchange_name']] )

                calculated_average_rates[currency]['last'] = calculated_average_rates[currency]['last'].quantize(DEC_PLACES)
                calculated_average_rates[currency]['ask'] = calculated_average_rates[currency]['ask'].quantize(DEC_PLACES)
                calculated_average_rates[currency]['bid'] = calculated_average_rates[currency]['bid'].quantize(DEC_PLACES)

    for currency in CURRENCY_LIST:
        calculated_average_rates[currency]['last'] = str(calculated_average_rates[currency]['last'])
        calculated_average_rates[currency]['ask'] = str(calculated_average_rates[currency]['ask'])
        calculated_average_rates[currency]['bid'] = str(calculated_average_rates[currency]['bid'])

        for exchange_name in EXCHANGE_LIST:
            if exchange_name in calculated_relative_volumes[currency]:
                calculated_relative_volumes[currency][exchange_name] = str(calculated_relative_volumes[currency][exchange_name])

    timestamp = utils.formatdate(time.time())
    try:
        all_data = {}
        all_data['timestamp'] = timestamp
        for currency in CURRENCY_LIST:
            cur_data = {'volumes': calculated_relative_volumes[currency],
                        'rates': calculated_average_rates[currency],
                        }
            all_data[currency] = cur_data

        api_all_data_file = open(os.path.join(project_abs_path, API_FILES['ALL_FILE']), 'w+')
        api_all_data_file.write(json.dumps(all_data,  indent=2, sort_keys=True, separators=(',', ': ')))
        api_all_data_file.close()

        rates_all = calculated_average_rates
        rates_all['timestamp'] = timestamp
        api_ticker_all_file = open(os.path.join(project_abs_path, API_FILES['TICKER_PATH'], 'all'), 'w+')
        api_ticker_all_file.write(json.dumps(rates_all, indent=2, sort_keys=True, separators=(',', ': ')))
        api_ticker_all_file.close()

        for currency in CURRENCY_LIST:
            ticker_cur = calculated_average_rates[currency]
            ticker_cur['timestamp'] = timestamp
            api_ticker_file = open(os.path.join(project_abs_path, API_FILES['TICKER_PATH'], currency), 'w+')
            api_ticker_file.write(json.dumps(ticker_cur,  indent=2, sort_keys=True, separators=(',', ': ')))
            api_ticker_file.close()

        volumes_all = calculated_relative_volumes
        volumes_all['timestamp'] = timestamp
        api_volume_all_file = open(os.path.join(project_abs_path, API_FILES['VOLUME_PATH'], 'all'), 'w+')
        api_volume_all_file.write(json.dumps(volumes_all, indent=2, sort_keys=True, separators=(',', ': ')))
        api_volume_all_file.close()

        for currency in CURRENCY_LIST:
            volume_cur = calculated_relative_volumes[currency]
            volume_cur['timestamp'] = timestamp
            api_ticker_file = open(os.path.join(project_abs_path, API_FILES['VOLUME_PATH'], currency), 'w+')
            api_ticker_file.write(json.dumps(volume_cur,  indent=2, sort_keys=True, separators=(',', ': ')))
            api_ticker_file.close()

        api_ignored_file = open(os.path.join(project_abs_path, API_FILES['IGNORED_FILE']), 'w+')
        api_ignored_file.write(json.dumps(exchanges_ignored,  indent=2, sort_keys=True, separators=(',', ': ')))
        api_ignored_file.close()

    except IOError as error:
        raise error
        continue

    print '----'

    time.sleep(API_QUERY_FREQUENCY)
