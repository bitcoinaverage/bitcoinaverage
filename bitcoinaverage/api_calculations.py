import os
import subprocess
import sys
import csv
from copy import deepcopy
import StringIO
from decimal import Decimal, InvalidOperation
import simplejson
from eventlet.green import urllib2
from eventlet.green import httplib
from eventlet.timeout import Timeout
import socket
import json

import bitcoinaverage as ba
import bitcoinaverage.server as server
from bitcoinaverage.config import DEC_PLACES, API_CALL_TIMEOUT_THRESHOLD, API_REQUEST_HEADERS, CURRENCY_LIST, API_FILES, EXCHANGE_LIST, INDEX_DOCUMENT_NAME
from bitcoinaverage.exceptions import CallTimeoutException
import bitcoinaverage.helpers as helpers


def get24hAverage(currency_code):
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
        return DEC_PLACES

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

def get24hGlobalAverage(currency_code):
    history_currency_API_24h_path = '%s%s/per_minute_24h_global_average_sliding_window.csv' % (ba.server.API_INDEX_URL_HISTORY, currency_code)

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
        return DEC_PLACES

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
            price_sum = price_sum + Decimal(row[len(row)-1])
            index = index + 1
        except (IndexError, InvalidOperation):
            continue
    try:
        average_price = (price_sum / Decimal(index)).quantize(DEC_PLACES)
    except InvalidOperation:
        average_price = DEC_PLACES

    return average_price

#calculates global average for all possible currencies
def calculateAllGlobalAverages(calculated_average_rates, total_currency_volumes):
    def getCurrencyCrossRate(currency_from, currency_to):
        if currency_from == currency_to:
            return Decimal(1)

        rate_from = Decimal(fiat_currencies_list[currency_from]['rate'])
        rate_to = Decimal(fiat_currencies_list[currency_to]['rate'])
        return (rate_from / rate_to)

    fiat_exchange_rates_url = server.API_INDEX_URL + 'fiat_data'
    try:
        with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
            result = urllib2.urlopen(urllib2.Request(url=fiat_exchange_rates_url, headers=API_REQUEST_HEADERS)).read()
            fiat_currencies_list = json.loads(result)
    except (KeyError,ValueError,socket.error,simplejson.decoder.JSONDecodeError,urllib2.URLError,httplib.BadStatusLine,CallTimeoutException):
        return {}, {}

    global_volume = DEC_PLACES
    for currency in CURRENCY_LIST:
        global_volume = global_volume + total_currency_volumes[currency]

    global_volume_percents = {}
    for currency in CURRENCY_LIST:
        global_volume_percents[currency] = (total_currency_volumes[currency] / global_volume * Decimal(100)).quantize(DEC_PLACES)

    global_averages = {}
    for currency_local in fiat_currencies_list:
        global_averages[currency_local] = {'last': DEC_PLACES,
                                           'ask': DEC_PLACES,
                                           'bid': DEC_PLACES,
                                            }
        for currency_to_convert in CURRENCY_LIST:
            global_averages[currency_local]['last'] = ( global_averages[currency_local]['last']
                                                + (calculated_average_rates[currency_to_convert]['last']
                                                   * global_volume_percents[currency_to_convert] / Decimal(100)
                                                   * getCurrencyCrossRate(currency_local, currency_to_convert) )
                                                        )
            global_averages[currency_local]['bid'] = ( global_averages[currency_local]['bid']
                                                + (calculated_average_rates[currency_to_convert]['bid']
                                                   * global_volume_percents[currency_to_convert] / Decimal(100)
                                                   * getCurrencyCrossRate(currency_local, currency_to_convert) )
                                                        )
            global_averages[currency_local]['ask'] = ( global_averages[currency_local]['ask']
                                                + (calculated_average_rates[currency_to_convert]['ask']
                                                   * global_volume_percents[currency_to_convert] / Decimal(100)
                                                   * getCurrencyCrossRate(currency_local, currency_to_convert) )
                                                        )
        global_averages[currency_local]['last'] = global_averages[currency_local]['last'].quantize(DEC_PLACES)
        global_averages[currency_local]['bid'] = global_averages[currency_local]['bid'].quantize(DEC_PLACES)
        global_averages[currency_local]['ask'] = global_averages[currency_local]['ask'].quantize(DEC_PLACES)
        currency_local_24h_avg = get24hGlobalAverage(currency_local)
        if currency_local_24h_avg > DEC_PLACES:
            global_averages[currency_local]['24h_avg'] = currency_local_24h_avg

    return global_averages, global_volume_percents


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

    for currency in CURRENCY_LIST:
        total_currency_volumes[currency] = total_currency_volumes[currency].quantize(DEC_PLACES)
        total_currency_volumes_ask[currency] = total_currency_volumes_ask[currency].quantize(DEC_PLACES)
        total_currency_volumes_bid[currency] = total_currency_volumes_bid[currency].quantize(DEC_PLACES)

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
                calculated_volumes[currency][rate['exchange_name']]['display_name'] = rate['exchange_display_name']
                try:
                    calculated_volumes[currency][rate['exchange_name']]['display_URL'] = rate['exchange_display_URL']
                except KeyError:
                    pass
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


def formatDataForAPI(calculated_average_rates, calculated_volumes, total_currency_volumes,
                     calculated_global_average_rates, calculated_global_volume_percents):
    for currency in CURRENCY_LIST:
        if currency in calculated_average_rates:
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
            try:
                calculated_average_rates[currency]['24h_avg'] = float(get24hAverage(currency))
            except TypeError:
                calculated_average_rates[currency]['24h_avg'] = str(get24hAverage(currency))

        for exchange_name in EXCHANGE_LIST:
            if currency in calculated_volumes and exchange_name in calculated_volumes[currency]:
                calculated_volumes[currency][exchange_name]['display_name'] = calculated_volumes[currency][exchange_name]['display_name']
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

    for currency in calculated_global_average_rates:
        try:
            calculated_global_average_rates[currency]['last'] = float(calculated_global_average_rates[currency]['last'])
        except TypeError:
            calculated_global_average_rates[currency]['last'] = str(calculated_global_average_rates[currency]['last'])
        try:
            calculated_global_average_rates[currency]['ask'] = float(calculated_global_average_rates[currency]['ask'])
        except TypeError:
            calculated_global_average_rates[currency]['ask'] = str(calculated_global_average_rates[currency]['ask'])
        try:
            calculated_global_average_rates[currency]['bid'] = float(calculated_global_average_rates[currency]['bid'])
        except TypeError:
            calculated_global_average_rates[currency]['bid'] = str(calculated_global_average_rates[currency]['bid'])
        try:
            calculated_global_average_rates[currency]['24h_avg'] = float(calculated_global_average_rates[currency]['24h_avg'])
        except TypeError:
            calculated_global_average_rates[currency]['24h_avg'] = str(calculated_global_average_rates[currency]['24h_avg'])
        except KeyError:
            pass

        if currency in CURRENCY_LIST:
            try:
                calculated_global_average_rates[currency]['volume_btc'] = float(total_currency_volumes[currency])
            except TypeError:
                calculated_global_average_rates[currency]['volume_btc'] = str(total_currency_volumes[currency])
            try:
                calculated_global_average_rates[currency]['volume_percent'] = float(calculated_global_volume_percents[currency])
            except TypeError:
                calculated_global_average_rates[currency]['volume_percent'] = str(calculated_global_volume_percents[currency])
        else:
            calculated_global_average_rates[currency]['volume_btc'] = 0.0
            calculated_global_average_rates[currency]['volume_percent'] = 0.0
    return calculated_average_rates, calculated_volumes, calculated_global_average_rates


def writeAPIFiles(api_path, timestamp, calculated_average_rates_formatted, calculated_volumes_formatted,
                  calculated_global_average_rates_formatted, exchanges_ignored):
    try:
        # /all
        all_data = {}
        all_data['timestamp'] = timestamp
        all_data['ignored_exchanges'] = exchanges_ignored
        for currency in CURRENCY_LIST:
            if (currency in calculated_volumes_formatted
            and currency in calculated_average_rates_formatted
            and currency in calculated_global_average_rates_formatted):
                cur_data = {'exchanges': calculated_volumes_formatted[currency],
                            'averages': calculated_average_rates_formatted[currency],
                            'global_averages': calculated_global_average_rates_formatted[currency],
                            }
                all_data[currency] = cur_data

        helpers.write_api_file(
            os.path.join(api_path, API_FILES['ALL_FILE']),
            json.dumps(all_data,  indent=2, sort_keys=True, separators=(',', ': ')))

        # /ticker/*
        for currency in CURRENCY_LIST:
            if (currency in calculated_volumes_formatted and currency in calculated_average_rates_formatted
            and currency in calculated_global_average_rates_formatted):
                ticker_cur = calculated_average_rates_formatted[currency]
                ticker_cur['timestamp'] = timestamp
                ticker_currency_path = os.path.join(api_path, API_FILES['TICKER_PATH'], currency)
                helpers.write_api_file(
                    os.path.join(ticker_currency_path, INDEX_DOCUMENT_NAME),
                    json.dumps(ticker_cur, indent=2, sort_keys=True, separators=(',', ': ')))
                for key in ticker_cur:
                    helpers.write_api_file(
                        os.path.join(ticker_currency_path, key),
                        str(ticker_cur[key]),
                        compress=False)

        # /ticker/all
        rates_all = calculated_average_rates_formatted
        rates_all['timestamp'] = timestamp
        helpers.write_api_file(
            os.path.join(api_path, API_FILES['TICKER_PATH'], 'all'),
            json.dumps(rates_all, indent=2, sort_keys=True, separators=(',', ': ')))

        # /ticker/global/*
        for currency in calculated_global_average_rates_formatted:
            ticker_cur = calculated_global_average_rates_formatted[currency]
            ticker_cur['timestamp'] = timestamp
            ticker_currency_path = os.path.join(api_path, API_FILES['GLOBAL_TICKER_PATH'], currency)
            helpers.write_api_file(
                os.path.join(ticker_currency_path, INDEX_DOCUMENT_NAME),
                json.dumps(ticker_cur, indent=2, sort_keys=True, separators=(',', ': ')))
            for key in ticker_cur:
                helpers.write_api_file(
                    os.path.join(ticker_currency_path, key),
                    str(ticker_cur[key]),
                    compress=False)

        # /ticker/global/all
        rates_all = calculated_global_average_rates_formatted
        rates_all['timestamp'] = timestamp
        try:
            helpers.write_api_file(
                os.path.join(api_path, API_FILES['GLOBAL_TICKER_PATH'], 'all'),
                json.dumps(rates_all, indent=2, sort_keys=True, separators=(',', ': ')))
        except IOError as error:
            #pass on Windows if there is currency with code ALL and it will interfer with file called 'all'
            pass

        # /exchanges/all
        volumes_all = calculated_volumes_formatted
        volumes_all['timestamp'] = timestamp
        helpers.write_api_file(
            os.path.join(api_path, API_FILES['EXCHANGES_PATH'], 'all'),
            json.dumps(volumes_all, indent=2, sort_keys=True, separators=(',', ': ')))

        # /exchanges/*
        for currency in CURRENCY_LIST:
            if (currency in calculated_volumes_formatted and currency in calculated_average_rates_formatted
                and currency in calculated_global_average_rates_formatted):
                volume_cur = calculated_volumes_formatted[currency]
                volume_cur['timestamp'] = timestamp
                helpers.write_api_file(
                    os.path.join(api_path, API_FILES['EXCHANGES_PATH'], currency),
                    json.dumps(volume_cur,  indent=2, sort_keys=True, separators=(',', ': ')))

        # /ignored
        helpers.write_api_file(
            os.path.join(api_path, API_FILES['IGNORED_FILE']),
            json.dumps(exchanges_ignored,  indent=2, sort_keys=True, separators=(',', ': ')))

    except IOError as error:
        error_text = '%s, %s ' % (sys.exc_info()[0], error)
        helpers.write_log(error_text, "ERROR")
        raise error
