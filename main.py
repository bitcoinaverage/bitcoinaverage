#!/usr/bin/python2.7
import os
import sys
from requests.exceptions import ConnectionError
from bitcoinaverage.exceptions import NoApiException, NoVolumeException, UnknownException

project_abs_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, project_abs_path)


import json
import time
from email import utils
from decimal import Decimal

from bitcoinaverage.config import EXCHANGE_LIST, CURRENCY_LIST, DEC_PLACES, API_QUERY_FREQUENCY, API_FILES, API_DOCUMENT_ROOT
from bitcoinaverage import api_parsers

if API_DOCUMENT_ROOT == '':
    API_DOCUMENT_ROOT = os.path.join(project_abs_path, 'api')


while True:

    exchanges_rates = []
    exchanges_ignored = {}

    for exchange_name in EXCHANGE_LIST:
        try:
            if not hasattr(api_parsers, exchange_name+'ApiCall'):
                raise NoApiException

            result = getattr(api_parsers, exchange_name+'ApiCall')(**EXCHANGE_LIST[exchange_name])

            if result is not None:
                result['exchange_name'] = exchange_name
                exchanges_rates.append(result)
            else:
                raise UnknownException
        except (NoApiException, NoVolumeException, UnknownException) as error:
            exchanges_ignored[exchange_name] = error.text
        except (ValueError, ConnectionError, TypeError) as error:
           pass

    calculated_average_rates = {}
    total_currency_volumes = {}
    calculated_volumes = {}
    for currency in CURRENCY_LIST:
        calculated_average_rates[currency] = {'last': DEC_PLACES,
                                               'ask': DEC_PLACES,
                                               'bid': DEC_PLACES,
                                                }
        total_currency_volumes[currency] = DEC_PLACES
        calculated_volumes[currency] = {}

    for rate in exchanges_rates:
        for currency in CURRENCY_LIST:
            if currency in rate:
                total_currency_volumes[currency] = total_currency_volumes[currency] + rate[currency]['volume']

    for rate in exchanges_rates:
        for currency in CURRENCY_LIST:
            if currency in rate:
                calculated_volumes[currency][rate['exchange_name']] = {}
                calculated_volumes[currency][rate['exchange_name']]['rates'] = {'ask': rate[currency]['ask'],
                                                                                'bid': rate[currency]['bid'],
                                                                                'last': rate[currency]['last'],
                                                                                    }
                if calculated_volumes[currency][rate['exchange_name']]['rates']['ask'] is not None:
                    calculated_volumes[currency][rate['exchange_name']]['rates']['ask'].quantize(DEC_PLACES)
                if calculated_volumes[currency][rate['exchange_name']]['rates']['bid'] is not None:
                    calculated_volumes[currency][rate['exchange_name']]['rates']['bid'].quantize(DEC_PLACES)
                if calculated_volumes[currency][rate['exchange_name']]['rates']['last'] is not None:
                    calculated_volumes[currency][rate['exchange_name']]['rates']['last'].quantize(DEC_PLACES)

                calculated_volumes[currency][rate['exchange_name']]['volume_btc'] = rate[currency]['volume'].quantize(DEC_PLACES)
                calculated_volumes[currency][rate['exchange_name']]['volume_percent'] = (rate[currency]['volume']
                    / total_currency_volumes[currency] * Decimal(100) ).quantize(DEC_PLACES)

    for rate in exchanges_rates:
        for currency in CURRENCY_LIST:
            if currency in rate:
                if rate[currency]['last'] is not None:
                    calculated_average_rates[currency]['last'] = ( calculated_average_rates[currency]['last']
                                                            + rate[currency]['last'] * calculated_volumes[currency][rate['exchange_name']]['volume_percent'] / Decimal(100) )
                if rate[currency]['ask'] is not None:
                    calculated_average_rates[currency]['ask'] = ( calculated_average_rates[currency]['ask']
                                                            + rate[currency]['ask'] * calculated_volumes[currency][rate['exchange_name']]['volume_percent'] / Decimal(100) )
                if rate[currency]['bid'] is not None:
                    calculated_average_rates[currency]['bid'] = ( calculated_average_rates[currency]['bid']
                                                            + rate[currency]['bid'] * calculated_volumes[currency][rate['exchange_name']]['volume_percent'] / Decimal(100) )

                calculated_average_rates[currency]['last'] = calculated_average_rates[currency]['last'].quantize(DEC_PLACES)
                calculated_average_rates[currency]['ask'] = calculated_average_rates[currency]['ask'].quantize(DEC_PLACES)
                calculated_average_rates[currency]['bid'] = calculated_average_rates[currency]['bid'].quantize(DEC_PLACES)

    for currency in CURRENCY_LIST:
        calculated_average_rates[currency]['last'] = str(calculated_average_rates[currency]['last'])
        calculated_average_rates[currency]['ask'] = str(calculated_average_rates[currency]['ask'])
        calculated_average_rates[currency]['bid'] = str(calculated_average_rates[currency]['bid'])

        for exchange_name in EXCHANGE_LIST:
            if exchange_name in calculated_volumes[currency]:
                calculated_volumes[currency][exchange_name]['rates']['last'] = str(calculated_volumes[currency][exchange_name]['rates']['last'])
                calculated_volumes[currency][exchange_name]['rates']['ask'] = str(calculated_volumes[currency][exchange_name]['rates']['ask'])
                calculated_volumes[currency][exchange_name]['rates']['bid'] = str(calculated_volumes[currency][exchange_name]['rates']['bid'])
                calculated_volumes[currency][exchange_name]['volume_btc'] = str(calculated_volumes[currency][exchange_name]['volume_btc'])
                calculated_volumes[currency][exchange_name]['volume_percent'] = str(calculated_volumes[currency][exchange_name]['volume_percent'])

    timestamp = utils.formatdate(time.time())
    try:
        all_data = {}
        all_data['timestamp'] = timestamp
        all_data['ignored_exchanges'] = exchanges_ignored
        for currency in CURRENCY_LIST:
            cur_data = {'exchanges': calculated_volumes[currency],
                        'averages': calculated_average_rates[currency],
                        }
            all_data[currency] = cur_data

        api_all_data_file = open(os.path.join(API_DOCUMENT_ROOT, API_FILES['ALL_FILE']), 'w+')
        api_all_data_file.write(json.dumps(all_data,  indent=2, sort_keys=True, separators=(',', ': ')))
        api_all_data_file.close()

        rates_all = calculated_average_rates
        rates_all['timestamp'] = timestamp
        api_ticker_all_file = open(os.path.join(API_DOCUMENT_ROOT, API_FILES['TICKER_PATH'], 'all'), 'w+')
        api_ticker_all_file.write(json.dumps(rates_all, indent=2, sort_keys=True, separators=(',', ': ')))
        api_ticker_all_file.close()

        for currency in CURRENCY_LIST:
            ticker_cur = calculated_average_rates[currency]
            ticker_cur['timestamp'] = timestamp
            api_ticker_file = open(os.path.join(API_DOCUMENT_ROOT, API_FILES['TICKER_PATH'], currency), 'w+')
            api_ticker_file.write(json.dumps(ticker_cur,  indent=2, sort_keys=True, separators=(',', ': ')))
            api_ticker_file.close()

        volumes_all = calculated_volumes
        volumes_all['timestamp'] = timestamp
        api_volume_all_file = open(os.path.join(API_DOCUMENT_ROOT, API_FILES['EXCHANGES_PATH'], 'all'), 'w+')
        api_volume_all_file.write(json.dumps(volumes_all, indent=2, sort_keys=True, separators=(',', ': ')))
        api_volume_all_file.close()

        for currency in CURRENCY_LIST:
            volume_cur = calculated_volumes[currency]
            volume_cur['timestamp'] = timestamp
            api_ticker_file = open(os.path.join(API_DOCUMENT_ROOT, API_FILES['EXCHANGES_PATH'], currency), 'w+')
            api_ticker_file.write(json.dumps(volume_cur,  indent=2, sort_keys=True, separators=(',', ': ')))
            api_ticker_file.close()

        api_ignored_file = open(os.path.join(API_DOCUMENT_ROOT, API_FILES['IGNORED_FILE']), 'w+')
        api_ignored_file.write(json.dumps(exchanges_ignored,  indent=2, sort_keys=True, separators=(',', ': ')))
        api_ignored_file.close()

    except IOError as error:
        continue

    print timestamp

    time.sleep(API_QUERY_FREQUENCY)
