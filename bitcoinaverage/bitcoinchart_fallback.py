import simplejson
import time
import socket
from decimal import Decimal

import requests
from requests.exceptions import ConnectionError

import bitcoinaverage as ba
from bitcoinaverage.config import BITCOIN_CHARTS_API_URL, DEC_PLACES, API_REQUEST_HEADERS


def fetchBitcoinChartsData():
    global ba

    if 'bitcoincharts' not in ba.api_parsers.API_QUERY_CACHE:
        ba.api_parsers.API_QUERY_CACHE['bitcoincharts'] = {'last_call_timestamp': 0,
                                            'result': None,
                                            'call_fail_count': 0,
                                               }

    current_timestamp = int(time.time())
    if (ba.api_parsers.API_QUERY_CACHE['bitcoincharts']['last_call_timestamp']+ba.api_parsers.API_QUERY_FREQUENCY['bitcoincharts'] > current_timestamp):
        result = ba.api_parsers.API_QUERY_CACHE['bitcoincharts']['result']
    else:
        #TODO, TODO, TODO-TODO-TODO TODO-TODO TODO-DO-DO-DO
        result = requests.get(BITCOIN_CHARTS_API_URL, verify=False, headers=API_REQUEST_HEADERS).json()

        ba.api_parsers.API_QUERY_CACHE['bitcoincharts'] = {'last_call_timestamp': current_timestamp,
                                            'result':result,
                                            'call_fail_count':0,
                                               }

    return result

def getData(bitcoincharts_symbols):
    bitcoincharts_data = fetchBitcoinChartsData()

    return_result = {}
    return_result['data_source'] = 'bitcoincharts'
    for api in bitcoincharts_data:
        for currency_code in bitcoincharts_symbols:
            if api['symbol'] == bitcoincharts_symbols[currency_code]:
                return_result[currency_code] = {'ask': Decimal(api['ask']).quantize(DEC_PLACES),
                                                'bid': Decimal(float(api['bid'])).quantize(DEC_PLACES),
                                                'last': Decimal(float(api['close'])).quantize(DEC_PLACES),
                                                'volume': Decimal(float(api['volume'])).quantize(DEC_PLACES),
                                                   }

    return return_result