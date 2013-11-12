import os
import sys
import csv
import StringIO
from decimal import Decimal, InvalidOperation
import decimal
import simplejson
from eventlet.green import urllib2
from eventlet.green import httplib
from eventlet.timeout import Timeout
import socket
import json

import bitcoinaverage as ba
from bitcoinaverage.config import DEC_PLACES, API_CALL_TIMEOUT_THRESHOLD, API_REQUEST_HEADERS, CURRENCY_LIST, API_FILES, EXCHANGE_LIST
from bitcoinaverage.exceptions import CallTimeoutException
import bitcoinaverage.helpers as helpers


def get24hAverage(currency_code):
    average_price = DEC_PLACES
    history_currency_API_24h_path = '%s%s/per_minute_24h_sliding_window.csv' % (ba.server.API_INDEX_URL_HISTORY, currency_code)

    try:
        with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
            csv_result = urllib2.urlopen(urllib2.Request(url=history_currency_API_24h_path, headers=API_REQUEST_HEADERS)).read()
    except (
            KeyError,
            ValueError,
            socket.error,
            simplejson.decoder.JSONDecodeError,
            urllib2.URLError,
            httplib.BadStatusLine,
            CallTimeoutException):
        return 0

    csvfile = StringIO.StringIO(csv_result)
    csvreader = csv.reader(csvfile, delimiter=',')
    price_sum = DEC_PLACES
    index = 0
    header_passed = False
    for row in csvreader:
        if not header_passed:
            header_passed = True
            continue
        try:
            price_sum = price_sum + Decimal(row[1])
            index = index + 1
        except (IndexError, InvalidOperation):
            continue
    try:
        average_price = (price_sum / Decimal(index)).quantize(DEC_PLACES)
    except InvalidOperation:
        average_price = DEC_PLACES

    return average_price


def calculateTotalVolumes(exchanges_rates):
    total_currency_volumes = {}
    total_currency_volumes_ask = {}
    total_currency_volumes_bid = {}
    for currency in CURRENCY_LIST:
        total_currency_volumes[currency] = DEC_PLACES
        total_currency_volumes_ask[currency] = DEC_PLACES
        total_currency_volumes_bid[currency] = DEC_PLACES

    for i, rate in enumerate(exchanges_rates):
        for currency in CURRENCY_LIST:
            if currency in rate:
                if rate[currency]['volume'] is not None and rate[currency]['volume'] > 0:
                    total_currency_volumes[currency] = total_currency_volumes[currency] + rate[currency]['volume']
                    if rate[currency]['ask'] is not None:
                        total_currency_volumes_ask[currency] = total_currency_volumes_ask[currency] + rate[currency]['volume']
                    if rate[currency]['bid'] is not None:
                        total_currency_volumes_bid[currency] = total_currency_volumes_bid[currency] + rate[currency]['volume']
                else:
                    pass
                    # del exchanges_rates[i][currency]
                    # i think we should not hide exchanges with 0 volume, it should be just zeroed, but still shown. @AlexyKot

    return total_currency_volumes, total_currency_volumes_ask, total_currency_volumes_bid

def calculateRelativeVolumes(exchanges_rates, total_currency_volumes, total_currency_volumes_ask, total_currency_volumes_bid):
    calculated_volumes = {}
    for currency in CURRENCY_LIST:
        calculated_volumes[currency] = {}

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

                if rate[currency]['volume'] is None:
                    rate[currency]['volume'] = DEC_PLACES
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

    return calculated_volumes

def calculateAverageRates(exchanges_rates, calculated_volumes):
    calculated_average_rates = {}
    for currency in CURRENCY_LIST:
        calculated_average_rates[currency] = {'last': DEC_PLACES,
                                               'ask': DEC_PLACES,
                                               'bid': DEC_PLACES,
                                                }

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

    return calculated_average_rates

def formatDataForAPI(calculated_average_rates, calculated_volumes, total_currency_volumes):
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
        if '24h_avg' in calculated_average_rates[currency]: #no present in nogox API
            try:
                calculated_average_rates[currency]['24h_avg'] = float(get24hAverage(currency))
            except TypeError:
                calculated_average_rates[currency]['24h_avg'] = str(get24hAverage(currency))

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

    return calculated_average_rates, calculated_volumes


def writeAPIFiles(api_path, timestamp, calculated_average_rates, calculated_volumes, exchanges_ignored):
    try:
        all_data = {}
        all_data['timestamp'] = timestamp
        all_data['ignored_exchanges'] = exchanges_ignored
        for currency in CURRENCY_LIST:
            cur_data = {'exchanges': calculated_volumes[currency],
                        'averages': calculated_average_rates[currency],
                        }
            all_data[currency] = cur_data

        with open(os.path.join(api_path, API_FILES['ALL_FILE']), 'w+') as api_all_data_file:
            api_all_data_file.write(json.dumps(all_data,  indent=2, sort_keys=True, separators=(',', ': ')))

        rates_all = calculated_average_rates
        rates_all['timestamp'] = timestamp
        with open(os.path.join(api_path, API_FILES['TICKER_PATH'], 'all'), 'w+') as api_ticker_all_file:
            api_ticker_all_file.write(json.dumps(rates_all, indent=2, sort_keys=True, separators=(',', ': ')))

        for currency in CURRENCY_LIST:
            ticker_cur = calculated_average_rates[currency]
            ticker_cur['timestamp'] = timestamp
            api_ticker_file = open(os.path.join(api_path, API_FILES['TICKER_PATH'], currency), 'w+')
            api_ticker_file.write(json.dumps(ticker_cur,  indent=2, sort_keys=True, separators=(',', ': ')))
            api_ticker_file.close()

        volumes_all = calculated_volumes
        volumes_all['timestamp'] = timestamp
        with open(os.path.join(api_path, API_FILES['EXCHANGES_PATH'], 'all'), 'w+') as api_volume_all_file:
            api_volume_all_file.write(json.dumps(volumes_all, indent=2, sort_keys=True, separators=(',', ': ')))

        for currency in CURRENCY_LIST:
            volume_cur = calculated_volumes[currency]
            volume_cur['timestamp'] = timestamp
            api_ticker_file = open(os.path.join(api_path, API_FILES['EXCHANGES_PATH'], currency), 'w+')
            api_ticker_file.write(json.dumps(volume_cur,  indent=2, sort_keys=True, separators=(',', ': ')))
            api_ticker_file.close()

        with open(os.path.join(api_path, API_FILES['IGNORED_FILE']), 'w+') as api_ignored_file:
            api_ignored_file.write(json.dumps(exchanges_ignored,  indent=2, sort_keys=True, separators=(',', ': ')))

    except IOError as error:
        error_text = '%s, %s ' % (sys.exc_info()[0], error)
        helpers.write_log(error_text)
        print 'ERROR: %s ' % (error_text)
        raise error


def createNogoxApi(timestamp, exchanges_rates, exchanges_ignored):
    for i, exchange_data in enumerate(exchanges_rates):
        if exchanges_rates[i]['exchange_name'] == 'mtgox':
            del exchanges_rates[i]['USD']
            del exchanges_rates[i]['GBP']
            del exchanges_rates[i]['EUR']

    calculated_average_rates = {}
    for currency in CURRENCY_LIST:
        calculated_average_rates[currency] = {'last': DEC_PLACES,
                                               'ask': DEC_PLACES,
                                               'bid': DEC_PLACES,
                                                }

    total_currency_volumes, total_currency_volumes_ask, total_currency_volumes_bid = calculateTotalVolumes(exchanges_rates)
    calculated_volumes = calculateRelativeVolumes(exchanges_rates,
                                                  total_currency_volumes,
                                                  total_currency_volumes_ask,
                                                  total_currency_volumes_bid)

    calculated_average_rates = calculateAverageRates(exchanges_rates, calculated_volumes)

    calculated_average_rates_formatted, calculated_volumes_formatted = formatDataForAPI(calculated_average_rates,
                                                                                        calculated_volumes,
                                                                                        total_currency_volumes)
    writeAPIFiles(ba.server.API_DOCUMENT_ROOT_NOGOX,
                  timestamp,
                  calculated_average_rates_formatted,
                  calculated_volumes_formatted,
                  exchanges_ignored)
