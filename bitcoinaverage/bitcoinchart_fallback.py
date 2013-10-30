import json
import time
from decimal import Decimal
from eventlet.green import urllib2
from eventlet.timeout import Timeout

import bitcoinaverage as ba
from bitcoinaverage.config import BITCOIN_CHARTS_API_URL, DEC_PLACES, API_REQUEST_HEADERS, API_CALL_TIMEOUT_THRESHOLD
from bitcoinaverage.exceptions import CallTimeoutException


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
        with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
            response = urllib2.urlopen(urllib2.Request(url=BITCOIN_CHARTS_API_URL, headers=API_REQUEST_HEADERS)).read()
            result = json.loads(response)

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
                try:
                    return_result[currency_code] = {'ask': Decimal(api['ask']).quantize(DEC_PLACES),
                                                    'bid': Decimal(float(api['bid'])).quantize(DEC_PLACES),
                                                    'last': Decimal(float(api['close'])).quantize(DEC_PLACES),
                                                    'volume': Decimal(float(api['volume'])).quantize(DEC_PLACES),
                                                       }
                except TypeError:
                    pass

    return return_result


