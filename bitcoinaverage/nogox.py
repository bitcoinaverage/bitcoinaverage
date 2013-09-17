import os
import sys
import json
from decimal import Decimal

import bitcoinaverage as ba
from bitcoinaverage.config import EXCHANGE_LIST, CURRENCY_LIST, DEC_PLACES, API_FILES
from bitcoinaverage.helpers import write_log
from bitcoinaverage import api_parsers, bitcoinchart_fallback
from bitcoinaverage.api_calculations import get24hAverage
from bitcoinaverage.exceptions import NoApiException, NoVolumeException, CallFailedException


def create_nogox_api(timestamp):
    exchanges_rates = []
    exchanges_ignored = {}

    for exchange_name in EXCHANGE_LIST:
        try:
            if api_parsers.hasAPI(exchange_name):
                result = api_parsers.callAPI(exchange_name=exchange_name, exchange_params=EXCHANGE_LIST[exchange_name])
            elif 'bitcoincharts_symbols' in EXCHANGE_LIST[exchange_name]:
                result = bitcoinchart_fallback.getData(EXCHANGE_LIST[exchange_name]['bitcoincharts_symbols'])
            else:
                raise NoApiException

            if result is not None:
                if exchange_name == 'mtgox':
                    result = result.copy()
                    del result['USD']
                    del result['GBP']
                    del result['EUR']
                result['exchange_name'] = exchange_name
                exchanges_rates.append(result)
            else:
                raise CallFailedException
        except (NoApiException, NoVolumeException, CallFailedException) as error:
            exchanges_ignored[exchange_name] = error.text


    calculated_average_rates = {}
    total_currency_volumes = {}
    total_currency_volumes_ask = {}
    total_currency_volumes_bid = {}
    calculated_volumes = {}
    for currency in CURRENCY_LIST:
        calculated_average_rates[currency] = {'last': DEC_PLACES,
                                               'ask': DEC_PLACES,
                                               'bid': DEC_PLACES,
                                                }
        total_currency_volumes[currency] = DEC_PLACES
        total_currency_volumes_ask[currency] = DEC_PLACES
        total_currency_volumes_bid[currency] = DEC_PLACES
        calculated_volumes[currency] = {}

    for rate in exchanges_rates:
        for currency in CURRENCY_LIST:
            if currency in rate:
                if rate[currency]['volume'] is None:
                    rate[currency]['volume'] = DEC_PLACES

                total_currency_volumes[currency] = total_currency_volumes[currency] + rate[currency]['volume']
                if rate[currency]['ask'] is not None:
                    total_currency_volumes_ask[currency] = total_currency_volumes_ask[currency] + rate[currency]['volume']
                if rate[currency]['bid'] is not None:
                    total_currency_volumes_bid[currency] = total_currency_volumes_bid[currency] + rate[currency]['volume']

    for rate in exchanges_rates:
        for currency in CURRENCY_LIST:
            if currency in rate:
                calculated_volumes[currency][rate['exchange_name']] = {}
                calculated_volumes[currency][rate['exchange_name']]['rates'] = {'ask': rate[currency]['ask'],
                                                                                'bid': rate[currency]['bid'],
                                                                                'last': rate[currency]['last'],
                                                                                    }
                calculated_volumes[currency][rate['exchange_name']]['source'] = rate['data_source']
                if calculated_volumes[currency][rate['exchange_name']]['rates']['last'] is not None:
                    calculated_volumes[currency][rate['exchange_name']]['rates']['last'].quantize(DEC_PLACES)
                calculated_volumes[currency][rate['exchange_name']]['volume_btc'] = rate[currency]['volume'].quantize(DEC_PLACES)
                if total_currency_volumes[currency] > 0:
                    calculated_volumes[currency][rate['exchange_name']]['volume_percent'] = (rate[currency]['volume']
                        / total_currency_volumes[currency] * Decimal(100) ).quantize(DEC_PLACES)
                else:
                    calculated_volumes[currency][rate['exchange_name']]['volume_percent'] = Decimal(0).quantize(DEC_PLACES)

                if calculated_volumes[currency][rate['exchange_name']]['rates']['ask'] is not None:
                    calculated_volumes[currency][rate['exchange_name']]['rates']['ask'].quantize(DEC_PLACES)
                    if total_currency_volumes[currency] > 0:
                        calculated_volumes[currency][rate['exchange_name']]['volume_percent_ask'] = (rate[currency]['volume']
                            / total_currency_volumes_ask[currency] * Decimal(100) ).quantize(DEC_PLACES)
                    else:
                        calculated_volumes[currency][rate['exchange_name']]['volume_percent_ask'] = Decimal(0).quantize(DEC_PLACES)

                if calculated_volumes[currency][rate['exchange_name']]['rates']['bid'] is not None:
                    calculated_volumes[currency][rate['exchange_name']]['rates']['bid'].quantize(DEC_PLACES)
                    if total_currency_volumes[currency] > 0:
                        calculated_volumes[currency][rate['exchange_name']]['volume_percent_bid'] = (rate[currency]['volume']
                            / total_currency_volumes_bid[currency] * Decimal(100) ).quantize(DEC_PLACES)
                    else:
                        calculated_volumes[currency][rate['exchange_name']]['volume_percent_bid'] = Decimal(0).quantize(DEC_PLACES)

    for rate in exchanges_rates:
        for currency in CURRENCY_LIST:
            if currency in rate:
                if rate[currency]['last'] is not None:
                    calculated_average_rates[currency]['last'] = ( calculated_average_rates[currency]['last']
                                                            + rate[currency]['last'] * calculated_volumes[currency][rate['exchange_name']]['volume_percent'] / Decimal(100) )
                if rate[currency]['ask'] is not None:
                    calculated_average_rates[currency]['ask'] = ( calculated_average_rates[currency]['ask']
                                                            + rate[currency]['ask'] * calculated_volumes[currency][rate['exchange_name']]['volume_percent_ask'] / Decimal(100) )
                if rate[currency]['bid'] is not None:
                    calculated_average_rates[currency]['bid'] = ( calculated_average_rates[currency]['bid']
                                                            + rate[currency]['bid'] * calculated_volumes[currency][rate['exchange_name']]['volume_percent_bid'] / Decimal(100) )

                calculated_average_rates[currency]['last'] = calculated_average_rates[currency]['last'].quantize(DEC_PLACES)
                calculated_average_rates[currency]['ask'] = calculated_average_rates[currency]['ask'].quantize(DEC_PLACES)
                calculated_average_rates[currency]['bid'] = calculated_average_rates[currency]['bid'].quantize(DEC_PLACES)

    for currency in CURRENCY_LIST:
        try:
            calculated_average_rates[currency]['last'] = float(calculated_average_rates[currency]['last'])
        except TypeError:
            calculated_average_rates[currency]['last'] = str(calculated_average_rates[currency]['last'])
        try:
            calculated_average_rates[currency]['ask'] = float(calculated_average_rates[currency]['ask'])
        except TypeError:
            calculated_average_rates[currency]['ask'] = str(calculated_average_rates[currency]['ask'])
        try:
            calculated_average_rates[currency]['bid'] = float(calculated_average_rates[currency]['bid'])
        except TypeError:
            calculated_average_rates[currency]['bid'] = str(calculated_average_rates[currency]['bid'])
        try:
            calculated_average_rates[currency]['total_vol'] = float(total_currency_volumes[currency])
        except TypeError:
            calculated_average_rates[currency]['total_vol'] = str(total_currency_volumes[currency])

        for exchange_name in EXCHANGE_LIST:
            if exchange_name in calculated_volumes[currency]:
                try:
                    calculated_volumes[currency][exchange_name]['rates']['last'] = float(calculated_volumes[currency][exchange_name]['rates']['last'])
                except TypeError:
                    calculated_volumes[currency][exchange_name]['rates']['last'] = str(calculated_volumes[currency][exchange_name]['rates']['last'])
                try:
                    calculated_volumes[currency][exchange_name]['rates']['ask'] = float(calculated_volumes[currency][exchange_name]['rates']['ask'])
                except TypeError:
                    calculated_volumes[currency][exchange_name]['rates']['ask'] = str(calculated_volumes[currency][exchange_name]['rates']['ask'])
                try:
                    calculated_volumes[currency][exchange_name]['rates']['bid'] = float(calculated_volumes[currency][exchange_name]['rates']['bid'])
                except TypeError:
                    calculated_volumes[currency][exchange_name]['rates']['bid'] = str(calculated_volumes[currency][exchange_name]['rates']['bid'])
                try:
                    calculated_volumes[currency][exchange_name]['volume_btc'] = float(calculated_volumes[currency][exchange_name]['volume_btc'])
                except TypeError:
                    calculated_volumes[currency][exchange_name]['volume_btc'] = str(calculated_volumes[currency][exchange_name]['volume_btc'])
                try:
                    calculated_volumes[currency][exchange_name]['volume_percent'] = float(calculated_volumes[currency][exchange_name]['volume_percent'])
                except TypeError:
                    calculated_volumes[currency][exchange_name]['volume_percent'] = str(calculated_volumes[currency][exchange_name]['volume_percent'])
                if 'volume_percent_ask' in calculated_volumes[currency][exchange_name]:
                    del calculated_volumes[currency][exchange_name]['volume_percent_ask']
                if 'volume_percent_bid' in calculated_volumes[currency][exchange_name]:
                    del calculated_volumes[currency][exchange_name]['volume_percent_bid']

    try:
        all_data = {}
        all_data['timestamp'] = timestamp
        all_data['ignored_exchanges'] = exchanges_ignored
        for currency in CURRENCY_LIST:
            cur_data = {'exchanges': calculated_volumes[currency],
                        'averages': calculated_average_rates[currency],
                        }
            all_data[currency] = cur_data

        with open(os.path.join(ba.server.API_DOCUMENT_ROOT_NOGOX, API_FILES['ALL_FILE']), 'w+') as api_all_data_file:
            api_all_data_file.write(json.dumps(all_data,  indent=2, sort_keys=True, separators=(',', ': ')))

        rates_all = calculated_average_rates
        rates_all['timestamp'] = timestamp
        with open(os.path.join(ba.server.API_DOCUMENT_ROOT_NOGOX, API_FILES['TICKER_PATH'], 'all'), 'w+') as api_ticker_all_file:
            api_ticker_all_file.write(json.dumps(rates_all, indent=2, sort_keys=True, separators=(',', ': ')))

        for currency in CURRENCY_LIST:
            ticker_cur = calculated_average_rates[currency]
            ticker_cur['timestamp'] = timestamp
            api_ticker_file = open(os.path.join(ba.server.API_DOCUMENT_ROOT_NOGOX, API_FILES['TICKER_PATH'], currency), 'w+')
            api_ticker_file.write(json.dumps(ticker_cur,  indent=2, sort_keys=True, separators=(',', ': ')))
            api_ticker_file.close()

        volumes_all = calculated_volumes
        volumes_all['timestamp'] = timestamp
        with open(os.path.join(ba.server.API_DOCUMENT_ROOT_NOGOX, API_FILES['EXCHANGES_PATH'], 'all'), 'w+') as api_volume_all_file:
            api_volume_all_file.write(json.dumps(volumes_all, indent=2, sort_keys=True, separators=(',', ': ')))

        for currency in CURRENCY_LIST:
            volume_cur = calculated_volumes[currency]
            volume_cur['timestamp'] = timestamp
            api_ticker_file = open(os.path.join(ba.server.API_DOCUMENT_ROOT_NOGOX, API_FILES['EXCHANGES_PATH'], currency), 'w+')
            api_ticker_file.write(json.dumps(volume_cur,  indent=2, sort_keys=True, separators=(',', ': ')))
            api_ticker_file.close()

        with open(os.path.join(ba.server.API_DOCUMENT_ROOT_NOGOX, API_FILES['IGNORED_FILE']), 'w+') as api_ignored_file:
            api_ignored_file.write(json.dumps(exchanges_ignored,  indent=2, sort_keys=True, separators=(',', ': ')))

    except IOError as error:
        error_text = '%s, %s ' % (sys.exc_info()[0], error)
        write_log(error_text)
        print 'ERROR: %s ' % (error_text)
        raise error

    #NO-MTGOX ends here
    ###################
