import email
import json
import time
from decimal import Decimal
import datetime
import eventlet
from eventlet.green import urllib2
from eventlet.timeout import Timeout
import simplejson
import socket

from eventlet.green import httplib
from eventlet.green import ssl

class HTTPSConnection(httplib.HTTPConnection):
    "This class allows communication via SSL."
    default_port = httplib.HTTPS_PORT

    def __init__(self, host, port=None, key_file=None, cert_file=None,
            strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
            source_address=None):
        httplib.HTTPConnection.__init__(self, host, port, strict, timeout,
                source_address)
        self.key_file = key_file
        self.cert_file = cert_file

    def connect(self):
        "Connect to a host on a given (SSL) port."
        sock = socket.create_connection((self.host, self.port),
                self.timeout, self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        # this is the only line we modified from the httplib.py file
        # we added the ssl_version variable
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_TLSv1)

#now we override the one in httplib
eventlet.green.httplib.HTTPSConnection = HTTPSConnection
# ssl_version corrections are done


from bitcoinaverage.bitcoinchart_fallback import getData
from bitcoinaverage.config import DEC_PLACES, API_QUERY_FREQUENCY, API_IGNORE_TIMEOUT, API_REQUEST_HEADERS, EXCHANGE_LIST, API_CALL_TIMEOUT_THRESHOLD
from bitcoinaverage.exceptions import CallTimeoutException, NoApiException, CacheTimeoutException, NoVolumeException
from bitcoinaverage.helpers import write_log

API_QUERY_CACHE = {} #holds last calls to APIs and last received data between calls

exchanges_rates = []
exchanges_ignored = {}

def callAll(ignore_mtgox=False):
    global EXCHANGE_LIST, exchanges_rates, exchanges_ignored
    pool = eventlet.GreenPool()

    exchanges_rates = []
    exchanges_ignored = {}

    for exchange_name, exchange_data, exchange_ignore_reason in pool.imap(callAPI, EXCHANGE_LIST):
        if exchange_ignore_reason is None:
            if exchange_data is not None:
                if ignore_mtgox and exchange_name == 'mtgox':
                    exchange_data = exchange_data.copy()
                    del exchange_data['USD']
                    del exchange_data['GBP']
                    del exchange_data['EUR']

                exchange_data['exchange_name'] = exchange_name
                exchanges_rates.append(exchange_data)
        else:
            exchanges_ignored[exchange_name] = exchange_ignore_reason
    return exchanges_rates, exchanges_ignored


def callAPI(exchange_name):
    global API_QUERY_CACHE, API_QUERY_FREQUENCY, API_IGNORE_TIMEOUT, EXCHANGE_LIST

    current_timestamp = int(time.time())
    result = None
    exchange_ignore_reason = None

    if exchange_name not in API_QUERY_CACHE:
        API_QUERY_CACHE[exchange_name] = {'last_call_timestamp': 0,
                                           'result': None,
                                           'call_fail_count': 0,
                                               }

    try:
        try:
            if (exchange_name in API_QUERY_FREQUENCY
                and API_QUERY_CACHE[exchange_name]['last_call_timestamp']+API_QUERY_FREQUENCY[exchange_name] > current_timestamp):
                result = API_QUERY_CACHE[exchange_name]['result']
            else:
                if '_%sApiCall' % exchange_name in globals():
                    result = globals()['_%sApiCall' % exchange_name](**EXCHANGE_LIST[exchange_name])
                    result['data_source'] = 'api'
                elif 'bitcoincharts_symbols' in EXCHANGE_LIST[exchange_name]:
                    result = getData(EXCHANGE_LIST[exchange_name]['bitcoincharts_symbols'])
                    result['data_source'] = 'bitcoincharts'
                else:
                    raise NoApiException

                API_QUERY_CACHE[exchange_name] = {'last_call_timestamp': current_timestamp,
                                                   'result':result,
                                                   'call_fail_count': 0,
                                                   }
        except (
                KeyError,
                ValueError,
                socket.error,
                simplejson.decoder.JSONDecodeError,
                urllib2.URLError,
                httplib.BadStatusLine,
                CallTimeoutException) as error:

            API_QUERY_CACHE[exchange_name]['call_fail_count'] = API_QUERY_CACHE[exchange_name]['call_fail_count'] + 1
            if (API_QUERY_CACHE[exchange_name]['last_call_timestamp']+API_IGNORE_TIMEOUT > current_timestamp):
                result = API_QUERY_CACHE[exchange_name]['result']
                result['data_source'] = 'cache'
                write_log('%s call failed, %s, %s fails in a row, using cache, cache age %ss'
                          % (exchange_name,
                             type(error).__name__,
                             str(API_QUERY_CACHE[exchange_name]['call_fail_count']),
                             str(current_timestamp-API_QUERY_CACHE[exchange_name]['last_call_timestamp']) ),
                          'WARNING')
            else:
                last_call_datetime = datetime.datetime.fromtimestamp(current_timestamp)
                today = datetime.datetime.now()
                if current_timestamp == 0:
                    datetime_str = today.strftime('%H:%M')
                elif last_call_datetime.day == today.day and last_call_datetime.month == today.month:
                    datetime_str = last_call_datetime.strftime('%H:%M')
                else :
                    datetime_str = last_call_datetime.strftime('%d %b, %H:%M')

                log_message = ('%s call failed, %s, %s fails in a row, last successful call at %s, cache timeout, exchange ignored'
                               % (exchange_name,
                                  type(error).__name__,
                                  str(API_QUERY_CACHE[exchange_name]['call_fail_count']),
                                  email.utils.formatdate(API_QUERY_CACHE[exchange_name]['last_call_timestamp']),
                                    ))
                write_log(log_message, 'ERROR')
                exception = CacheTimeoutException()
                exception.text = exception.strerror % datetime_str
                raise exception
    except (NoApiException, NoVolumeException, CacheTimeoutException):
        exchange_ignore_reason = error.strerror

    return exchange_name, result, exchange_ignore_reason


def _mtgoxApiCall(usd_api_url, eur_api_url, gbp_api_url, cad_api_url, pln_api_url, rub_api_url, aud_api_url, chf_api_url,
                  cny_api_url, dkk_api_url, hkd_api_url, jpy_api_url, nzd_api_url, sgd_api_url, sek_api_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=usd_api_url, headers=API_REQUEST_HEADERS)).read()
        usd_result = json.loads(response)

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=eur_api_url, headers=API_REQUEST_HEADERS)).read()
        eur_result = json.loads(response)

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=gbp_api_url, headers=API_REQUEST_HEADERS)).read()
        gbp_result = json.loads(response)

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=cad_api_url, headers=API_REQUEST_HEADERS)).read()
        cad_result = json.loads(response)

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=pln_api_url, headers=API_REQUEST_HEADERS)).read()
        pln_result = json.loads(response)

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=rub_api_url, headers=API_REQUEST_HEADERS)).read()
        rub_result = json.loads(response)

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=aud_api_url, headers=API_REQUEST_HEADERS)).read()
        aud_result = json.loads(response)

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=chf_api_url, headers=API_REQUEST_HEADERS)).read()
        chf_result = json.loads(response)

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=cny_api_url, headers=API_REQUEST_HEADERS)).read()
        cny_result = json.loads(response)

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=dkk_api_url, headers=API_REQUEST_HEADERS)).read()
        dkk_result = json.loads(response)

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=hkd_api_url, headers=API_REQUEST_HEADERS)).read()
        hkd_result = json.loads(response)

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=jpy_api_url, headers=API_REQUEST_HEADERS)).read()
        jpy_result = json.loads(response)

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=nzd_api_url, headers=API_REQUEST_HEADERS)).read()
        nzd_result = json.loads(response)

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=sgd_api_url, headers=API_REQUEST_HEADERS)).read()
        sgd_result = json.loads(response)

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=sek_api_url, headers=API_REQUEST_HEADERS)).read()
        sek_result = json.loads(response)

    return {'USD': {'ask': Decimal(usd_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(usd_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(usd_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(usd_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'EUR': {'ask': Decimal(eur_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(eur_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(eur_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(eur_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'GBP': {'ask': Decimal(gbp_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(gbp_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(gbp_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(gbp_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'CAD': {'ask': Decimal(cad_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(cad_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(cad_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(cad_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'PLN': {'ask': Decimal(pln_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(pln_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(pln_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(pln_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'RUB': {'ask': Decimal(rub_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(rub_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(rub_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(rub_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'AUD': {'ask': Decimal(aud_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(aud_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(aud_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(aud_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'CHF': {'ask': Decimal(chf_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(chf_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(chf_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(chf_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'CNY': {'ask': Decimal(cny_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(cny_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(cny_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(cny_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'DKK': {'ask': Decimal(dkk_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(dkk_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(dkk_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(dkk_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'HKD': {'ask': Decimal(hkd_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(hkd_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(hkd_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(hkd_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'JPY': {'ask': Decimal(jpy_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(jpy_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(jpy_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(jpy_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'NZD': {'ask': Decimal(nzd_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(nzd_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(nzd_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(nzd_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'SGD': {'ask': Decimal(sgd_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(sgd_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(sgd_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(sgd_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'SEK': {'ask': Decimal(sek_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(sek_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(sek_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(sek_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
    }


def _bitstampApiCall(api_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=api_url, headers=API_REQUEST_HEADERS)).read()
        result = json.loads(response)

    return {'USD': {'ask': Decimal(result['ask']).quantize(DEC_PLACES),
                    'bid': Decimal(result['bid']).quantize(DEC_PLACES),
                    'last': Decimal(result['last']).quantize(DEC_PLACES),
                    'volume': Decimal(result['volume']).quantize(DEC_PLACES),
    }}

# direct volume calculation gives weird results, bitcoincharts API used for now
#@TODO check with campbx why their API results are incorrect
# def campbxApiCall(api_ticker_url, api_trades_url, *args, **kwargs):
#     ticker_result = requests.get(api_ticker_url, headers=API_REQUEST_HEADERS).json()
#
#     return_data = {'USD': {'ask': Decimal(ticker_result['Best Ask']).quantize(DEC_PLACES),
#                                            'bid': Decimal(ticker_result['Best Bid']).quantize(DEC_PLACES),
#                                            'last': Decimal(ticker_result['Last Trade']).quantize(DEC_PLACES),
#                                            'high': None,
#                                            'low': None,
#                                            }
#                     }
#
#     from_time = int(time.time())-(86400)
#     volume = 0.0
#
#     all_trades_direct = {}
#
#     while True:
#         trades = requests.get(api_trades_url % from_time, headers=API_REQUEST_HEADERS).json()
#         new_from_time = from_time
#         for trade in trades:
#             if trade['Time'] > new_from_time:
#                 all_trades_direct[trade['Order ID']] = {'time': trade['Time'],
#                                                          'volume': trade['Bitcoins'],
#                                                          'price': trade['Price'],
#                                                          }
#                 new_from_time = trade['Time']
#                 volume = volume + float(trade['Bitcoins'])
#
#         if new_from_time == from_time:
#             break
#         else:
#             from_time = new_from_time
#
#     return_data['USD']]['volume'] = Decimal(volume).quantize(DEC_PLACES)
#
#     return return_data


def _btceApiCall(usd_api_url, eur_api_url, rur_api_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=usd_api_url, headers=API_REQUEST_HEADERS)).read()
        usd_result = json.loads(response)
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=eur_api_url, headers=API_REQUEST_HEADERS)).read()
        eur_result = json.loads(response)
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=rur_api_url, headers=API_REQUEST_HEADERS)).read()
        rur_result = json.loads(response)

    #dirty hack, BTC-e has a bug in their APIs - buy/sell prices mixed up
    if usd_result['ticker']['sell'] < usd_result['ticker']['buy']:
        temp = usd_result['ticker']['buy']
        usd_result['ticker']['buy'] = usd_result['ticker']['sell']
        usd_result['ticker']['sell'] = temp

    if eur_result['ticker']['sell'] < eur_result['ticker']['buy']:
        temp = eur_result['ticker']['buy']
        eur_result['ticker']['buy'] = eur_result['ticker']['sell']
        eur_result['ticker']['sell'] = temp

    if rur_result['ticker']['sell'] < rur_result['ticker']['buy']:
        temp = rur_result['ticker']['buy']
        rur_result['ticker']['buy'] = rur_result['ticker']['sell']
        rur_result['ticker']['sell'] = temp

    return {'USD': {'ask': Decimal(usd_result['ticker']['sell']).quantize(DEC_PLACES),
                    'bid': Decimal(usd_result['ticker']['buy']).quantize(DEC_PLACES),
                    'last': Decimal(usd_result['ticker']['last']).quantize(DEC_PLACES),
                    'volume': Decimal(usd_result['ticker']['vol_cur']).quantize(DEC_PLACES),
                    },
            'EUR': {'ask': Decimal(eur_result['ticker']['sell']).quantize(DEC_PLACES),
                    'bid': Decimal(eur_result['ticker']['buy']).quantize(DEC_PLACES),
                    'last': Decimal(eur_result['ticker']['last']).quantize(DEC_PLACES),
                    'volume': Decimal(eur_result['ticker']['vol_cur']).quantize(DEC_PLACES),
            },
            'RUB': {'ask': Decimal(rur_result['ticker']['sell']).quantize(DEC_PLACES),
                    'bid': Decimal(rur_result['ticker']['buy']).quantize(DEC_PLACES),
                    'last': Decimal(rur_result['ticker']['last']).quantize(DEC_PLACES),
                    'volume': Decimal(rur_result['ticker']['vol_cur']).quantize(DEC_PLACES),
            }}


def _bitcurexApiCall(eur_ticker_url, eur_trades_url, pln_ticker_url, pln_trades_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=eur_ticker_url, headers=API_REQUEST_HEADERS)).read()
        eur_result = json.loads(response)
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=pln_ticker_url, headers=API_REQUEST_HEADERS)).read()
        pln_result = json.loads(response)

    last24h_time = int(time.time())-86400  #86400s in 24h
    eur_vol = 0.0

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=eur_trades_url, headers=API_REQUEST_HEADERS)).read()
        eur_volume_result = json.loads(response)
    for trade in eur_volume_result:
        if trade['date'] > last24h_time:
            eur_vol = eur_vol + float(trade['amount'])

    pln_vol = 0.0
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=pln_trades_url, headers=API_REQUEST_HEADERS)).read()
        pln_volume_result = json.loads(response)
    for trade in pln_volume_result:
        if trade['date'] > last24h_time:
            pln_vol = pln_vol + float(trade['amount'])

    return {'EUR': {'ask': Decimal(eur_result['sell']).quantize(DEC_PLACES),
                    'bid': Decimal(eur_result['buy']).quantize(DEC_PLACES),
                    'last': Decimal(eur_result['last']).quantize(DEC_PLACES),
                    'volume': Decimal(eur_vol).quantize(DEC_PLACES),
                    },
            'PLN': {'ask': Decimal(pln_result['sell']).quantize(DEC_PLACES),
                    'bid': Decimal(pln_result['buy']).quantize(DEC_PLACES),
                    'last': Decimal(pln_result['last']).quantize(DEC_PLACES),
                    'volume': Decimal(pln_vol).quantize(DEC_PLACES),
                    },
            }


def _vircurexApiCall(usd_api_url, eur_api_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=usd_api_url, headers=API_REQUEST_HEADERS)).read()
        usd_result = json.loads(response)

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=eur_api_url, headers=API_REQUEST_HEADERS)).read()
        eur_result = json.loads(response)

    return {'USD': {'ask': Decimal(usd_result['lowest_ask']).quantize(DEC_PLACES),
                    'bid': Decimal(usd_result['highest_bid']).quantize(DEC_PLACES),
                    'last': Decimal(usd_result['last_trade']).quantize(DEC_PLACES),
                    'volume': Decimal(usd_result['volume']).quantize(DEC_PLACES),
                    },
            'EUR': {'ask': Decimal(eur_result['lowest_ask']).quantize(DEC_PLACES),
                    'bid': Decimal(eur_result['highest_bid']).quantize(DEC_PLACES),
                    'last': Decimal(eur_result['last_trade']).quantize(DEC_PLACES),
                    'volume': Decimal(eur_result['volume']).quantize(DEC_PLACES),
            },
    }

def _bitbargainApiCall(gbp_api_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=gbp_api_url, headers=API_REQUEST_HEADERS)).read()
        gbp_result = json.loads(response)

    if gbp_result['response']['avg_24h'] is not None and gbp_result['response']['vol_24h'] is not None :
        average_btc = Decimal(gbp_result['response']['avg_24h'])
        volume_btc = (Decimal(gbp_result['response']['vol_24h']) / average_btc)
    else:
        average_btc = DEC_PLACES
        volume_btc = DEC_PLACES

    return {'GBP': {'ask': average_btc.quantize(DEC_PLACES), #bitbargain is an OTC trader, so ask == last
                    'bid': None, #bitbargain is an OTC trader, so no bids available
                    'last': average_btc.quantize(DEC_PLACES),
                    'volume': volume_btc.quantize(DEC_PLACES),
                    },
    }

def _localbitcoinsApiCall(api_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=api_url, headers=API_REQUEST_HEADERS)).read()
        result = json.loads(response)

    result = {}

    try:
        usd_volume = Decimal(result['USD']['volume_btc']).quantize(DEC_PLACES)
        if result['USD']['avg_3h'] is not None:
            usd_rate = Decimal(result['USD']['avg_3h']).quantize(DEC_PLACES)
        elif result['USD']['avg_12h'] is not None:
            usd_rate = Decimal(result['USD']['avg_12h']).quantize(DEC_PLACES)
        else:
            usd_rate = None
            usd_volume = None
        result['USD']= {'ask': usd_rate,
                        'bid': None,
                        'last': usd_rate,
                        'volume': usd_volume,
                        }
    except KeyError:
        pass

    try:
        eur_volume = Decimal(result['EUR']['volume_btc']).quantize(DEC_PLACES)
        if result['EUR']['avg_3h'] is not None:
            eur_rate = Decimal(result['EUR']['avg_3h']).quantize(DEC_PLACES)
        elif result['EUR']['avg_12h'] is not None:
            eur_rate = Decimal(result['EUR']['avg_12h']).quantize(DEC_PLACES)
        else:
            eur_volume = None
            eur_rate = None
        result['USD']= {'ask': eur_rate,
                        'bid': None,
                        'last': eur_rate,
                        'volume': eur_volume,
                        }
    except KeyError:
        pass

    try:
        gbp_volume = Decimal(result['GBP']['volume_btc']).quantize(DEC_PLACES)
        if result['GBP']['avg_3h'] is not None:
            gbp_rate = Decimal(result['GBP']['avg_3h']).quantize(DEC_PLACES)
        elif result['GBP']['avg_12h'] is not None:
            gbp_rate = Decimal(result['GBP']['avg_12h']).quantize(DEC_PLACES)
        else:
            gbp_volume = None
            gbp_rate = None
        result['USD']= {'ask': gbp_rate,
                        'bid': None,
                        'last': gbp_rate,
                        'volume': gbp_volume,
                        }
    except KeyError:
        pass

    try:
        cad_volume = Decimal(result['CAD']['volume_btc']).quantize(DEC_PLACES)
        if result['CAD']['avg_3h'] is not None:
            cad_rate = Decimal(result['CAD']['avg_3h']).quantize(DEC_PLACES)
        elif result['CAD']['avg_12h'] is not None:
            cad_rate = Decimal(result['CAD']['avg_12h']).quantize(DEC_PLACES)
        else:
            cad_volume = None
            cad_rate = None
        result['USD']= {'ask': cad_rate,
                        'bid': None,
                        'last': cad_rate,
                        'volume': cad_volume,
                        }
    except KeyError:
        pass

    try:
        nok_volume = Decimal(result['NOK']['volume_btc']).quantize(DEC_PLACES)
        if result['NOK']['avg_3h'] is not None:
            nok_rate = Decimal(result['NOK']['avg_3h']).quantize(DEC_PLACES)
        elif result['NOK']['avg_12h'] is not None:
            nok_rate = Decimal(result['NOK']['avg_12h']).quantize(DEC_PLACES)
        else:
            nok_volume = None
            nok_rate = None
        result['USD']= {'ask': nok_rate,
                        'bid': None,
                        'last': nok_rate,
                        'volume': nok_volume,
                        }
    except KeyError:
        pass

    try:
        nzd_volume = Decimal(result['NZD']['volume_btc']).quantize(DEC_PLACES)
        if result['NZD']['avg_3h'] is not None:
            nzd_rate = Decimal(result['NZD']['avg_3h']).quantize(DEC_PLACES)
        elif result['NZD']['avg_12h'] is not None:
            nzd_rate = Decimal(result['NZD']['avg_12h']).quantize(DEC_PLACES)
        else:
            nzd_volume = None
            nzd_rate = None
        result['USD']= {'ask': nzd_rate,
                        'bid': None,
                        'last': nzd_rate,
                        'volume': nzd_volume,
                        }
    except KeyError:
        pass

    try:
        zar_volume = Decimal(result['ZAR']['volume_btc']).quantize(DEC_PLACES)
        if result['ZAR']['avg_3h'] is not None:
            zar_rate = Decimal(result['ZAR']['avg_3h']).quantize(DEC_PLACES)
        elif result['ZAR']['avg_12h'] is not None:
            zar_rate = Decimal(result['ZAR']['avg_12h']).quantize(DEC_PLACES)
        else:
            zar_volume = None
            zar_rate = None
        result['USD']= {'ask': zar_rate,
                        'bid': None,
                        'last': zar_rate,
                        'volume': zar_volume,
                        }
    except KeyError:
        pass

    try:
        sek_volume = Decimal(result['SEK']['volume_btc']).quantize(DEC_PLACES)
        if result['SEK']['avg_3h'] is not None:
            sek_rate = Decimal(result['SEK']['avg_3h']).quantize(DEC_PLACES)
        elif result['SEK']['avg_12h'] is not None:
            sek_rate = Decimal(result['SEK']['avg_12h']).quantize(DEC_PLACES)
        else:
            sek_volume = None
            sek_rate = None
        result['USD']= {'ask': sek_rate,
                        'bid': None,
                        'last': sek_rate,
                        'volume': sek_volume,
                        }
    except KeyError:
        pass

    try:
        aud_volume = Decimal(result['AUD']['volume_btc']).quantize(DEC_PLACES)
        if result['AUD']['avg_3h'] is not None:
            aud_rate = Decimal(result['AUD']['avg_3h']).quantize(DEC_PLACES)
        elif result['AUD']['avg_12h'] is not None:
            aud_rate = Decimal(result['AUD']['avg_12h']).quantize(DEC_PLACES)
        else:
            aud_volume = None
            aud_rate = None
        result['USD']= {'ask': aud_rate,
                        'bid': None,
                        'last': aud_rate,
                        'volume': aud_volume,
                        }
    except KeyError:
        pass

    return result



def _cryptotradeApiCall(usd_api_url, #eur_api_url,
                        *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=usd_api_url, headers=API_REQUEST_HEADERS)).read()
        usd_result = json.loads(response)
    # with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
    #     response = urllib2.urlopen(urllib2.Request(url=eur_api_url, headers=API_REQUEST_HEADERS)).read()
    #     eur_result = json.loads(response)


    return {'USD': {'ask': Decimal(usd_result['data']['min_ask']).quantize(DEC_PLACES),
                    'bid': Decimal(usd_result['data']['max_bid']).quantize(DEC_PLACES),
                    'last': Decimal(usd_result['data']['last']).quantize(DEC_PLACES),
                    'volume': Decimal(usd_result['data']['vol_btc']).quantize(DEC_PLACES),
                                    },
            # 'EUR': {'ask': Decimal(eur_result['data']['min_ask']).quantize(DEC_PLACES),
            #         'bid': Decimal(eur_result['data']['max_bid']).quantize(DEC_PLACES),
            #         'last': Decimal(eur_result['data']['last']).quantize(DEC_PLACES),
            #         'volume': Decimal(eur_result['data']['vol_btc']).quantize(DEC_PLACES),
            #                         },
            }

def _rocktradingApiCall(#usd_ticker_url, usd_trades_url,
                        eur_ticker_url, eur_trades_url, *args, **kwargs):
    last24h_time = int(time.time())-86400  #86400s in 24h

    # with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
    #     response = urllib2.urlopen(urllib2.Request(url=usd_ticker_url, headers=API_REQUEST_HEADERS)).read()
    #     usd_ticker_result = json.loads(response)
    # with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
    #     response = urllib2.urlopen(urllib2.Request(url=usd_trades_url, headers=API_REQUEST_HEADERS)).read()
    #     usd_volume_result = json.loads(response)
    # usd_last = 0.0
    # usd_vol = 0.0
    # for trade in usd_volume_result:
    #     if trade['date'] > last24h_time:
    #         usd_vol = usd_vol + float(trade['price'])
    #         usd_last = float(trade['price'])

    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=eur_ticker_url, headers=API_REQUEST_HEADERS)).read()
        eur_ticker_result = json.loads(response)
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=eur_trades_url, headers=API_REQUEST_HEADERS)).read()
        eur_volume_result = json.loads(response)
    eur_last = 0.0
    eur_vol = 0.0
    for trade in eur_volume_result:
        if trade['date'] > last24h_time:
            eur_vol = eur_vol + float(trade['amount'])
            eur_last = float(trade['price'])

    return {
            # 'USD': {'ask': Decimal(usd_ticker_result['result'][0]['ask']).quantize(DEC_PLACES),
            #         'bid': Decimal(usd_ticker_result['result'][0]['bid']).quantize(DEC_PLACES),
            #         'high': Decimal(usd_high).quantize(DEC_PLACES),
            #         'low': Decimal(usd_low).quantize(DEC_PLACES),
            #         'last': Decimal(usd_last).quantize(DEC_PLACES),
            #         'avg': None,
            #         'volume': Decimal(usd_vol).quantize(DEC_PLACES),
            #                         },
            'EUR': {'ask': Decimal(eur_ticker_result['result'][0]['ask']).quantize(DEC_PLACES) if eur_ticker_result['result'][0]['ask'] is not None else None,
                    'bid': Decimal(eur_ticker_result['result'][0]['bid']).quantize(DEC_PLACES) if eur_ticker_result['result'][0]['bid'] is not None else None,
                    'last': Decimal(eur_last).quantize(DEC_PLACES),
                    'volume': Decimal(eur_vol).quantize(DEC_PLACES),
                                    },
            }

def _bitcashApiCall(czk_api_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=czk_api_url, headers=API_REQUEST_HEADERS)).read()
        czk_result = json.loads(response)

    return {'CZK': {'ask': Decimal(czk_result['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(czk_result['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(czk_result['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(czk_result['data']['vol']['value']).quantize(DEC_PLACES),
                    },
            }

def _intersangoApiCall(ticker_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=ticker_url, headers=API_REQUEST_HEADERS)).read()
        result = json.loads(response)

    #'2' in here is ID for EUR in intersango terms
    return {'EUR': {'ask': Decimal(result['2']['sell']).quantize(DEC_PLACES) if result['2']['sell'] is not None else None,
                    'bid': Decimal(result['2']['buy']).quantize(DEC_PLACES) if result['2']['buy'] is not None else None,
                    'last': Decimal(result['2']['last']).quantize(DEC_PLACES) if result['2']['last'] is not None else None,
                    'volume': Decimal(result['2']['vol']).quantize(DEC_PLACES) if result['2']['vol'] is not None else DEC_PLACES,
                    },
            }


def _bit2cApiCall(ticker_url, orders_url, trades_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=ticker_url, headers=API_REQUEST_HEADERS)).read()
        ticker = json.loads(response)
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=orders_url, headers=API_REQUEST_HEADERS)).read()
        orders = json.loads(response)
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=trades_url, headers=API_REQUEST_HEADERS)).read()
        trades = json.loads(response)

    last24h_time = int(time.time())-86400  #86400s in 24h
    volume = 0
    for trade in trades:
        if trade['date'] > last24h_time:
            volume = volume + float(trade['amount'])

    return {'ILS': {'ask': Decimal(orders['asks'][0][0]).quantize(DEC_PLACES),
                    'bid': Decimal(orders['bids'][0][0]).quantize(DEC_PLACES),
                    'last': Decimal(ticker['ll']).quantize(DEC_PLACES),
                    'volume': Decimal(volume).quantize(DEC_PLACES),
                    },
            }

def _kapitonApiCall(ticker_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=ticker_url, headers=API_REQUEST_HEADERS)).read()
        ticker = json.loads(response)

    return {'SEK': {'ask': Decimal(ticker['ask']).quantize(DEC_PLACES),
                    'bid': Decimal(ticker['bid']).quantize(DEC_PLACES),
                    'last': Decimal(ticker['price']).quantize(DEC_PLACES),
                    'volume': Decimal(ticker['vol']).quantize(DEC_PLACES),
                    },
            }


def _rmbtbApiCall(ticker_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=ticker_url, headers=API_REQUEST_HEADERS)).read()
        ticker = json.loads(response)

    return {'CNY': {'ask': Decimal(ticker['data']['sell']['value']).quantize(DEC_PLACES),
                    'bid': Decimal(ticker['data']['buy']['value']).quantize(DEC_PLACES),
                    'last': Decimal(ticker['data']['last']['value']).quantize(DEC_PLACES),
                    'volume': Decimal(ticker['data']['vol']['value']).quantize(DEC_PLACES),
                    },
            }

def _btcchinaApiCall(ticker_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=ticker_url, headers=API_REQUEST_HEADERS)).read()
        ticker = json.loads(response)

    return {'CNY': {'ask': Decimal(ticker['ticker']['sell']).quantize(DEC_PLACES),
                    'bid': Decimal(ticker['ticker']['buy']).quantize(DEC_PLACES),
                    'last': Decimal(ticker['ticker']['last']).quantize(DEC_PLACES),
                    'volume': Decimal(ticker['ticker']['vol']).quantize(DEC_PLACES),
                    },
            }


def _fxbtcApiCall(ticker_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=ticker_url, headers=API_REQUEST_HEADERS)).read()
        ticker = json.loads(response)

    return {'CNY': {'ask': Decimal(ticker['ticker']['ask']).quantize(DEC_PLACES),
                    'bid': Decimal(ticker['ticker']['bid']).quantize(DEC_PLACES),
                    'last': Decimal(ticker['ticker']['last_rate']).quantize(DEC_PLACES),
                    'volume': Decimal(ticker['ticker']['vol']).quantize(DEC_PLACES),
                    },
            }


def _bterApiCall(ticker_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=ticker_url, headers=API_REQUEST_HEADERS)).read()
        ticker = json.loads(response)

    return {'CNY': {'ask': Decimal(ticker['sell']).quantize(DEC_PLACES),
                    'bid': Decimal(ticker['buy']).quantize(DEC_PLACES),
                    'last': Decimal(ticker['last']).quantize(DEC_PLACES),
                    'volume': Decimal(ticker['vol_btc']).quantize(DEC_PLACES),
                    },
            }


def _goxbtcApiCall(ticker_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=ticker_url, headers=API_REQUEST_HEADERS)).read()
        ticker = json.loads(response)

    return {'CNY': {'ask': Decimal(ticker['sell']).quantize(DEC_PLACES),
                    'bid': Decimal(ticker['buy']).quantize(DEC_PLACES),
                    'last': Decimal(ticker['last']).quantize(DEC_PLACES),
                    'volume': Decimal(ticker['vol']).quantize(DEC_PLACES),
                    },
            }


def _okcoinApiCall(ticker_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=ticker_url, headers=API_REQUEST_HEADERS)).read()
        ticker = json.loads(response)

    return {'CNY': {'ask': Decimal(ticker['ticker']['sell']).quantize(DEC_PLACES),
                    'bid': Decimal(ticker['ticker']['buy']).quantize(DEC_PLACES),
                    'last': Decimal(ticker['ticker']['last']).quantize(DEC_PLACES),
                    'volume': Decimal(ticker['ticker']['vol']).quantize(DEC_PLACES),
                    },
            }

def _mercadoApiCall(ticker_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=ticker_url, headers=API_REQUEST_HEADERS)).read()
        ticker = json.loads(response)

    return {'BRL': {'ask': Decimal(ticker['ticker']['sell']).quantize(DEC_PLACES),
                    'bid': Decimal(ticker['ticker']['buy']).quantize(DEC_PLACES),
                    'last': Decimal(ticker['ticker']['last']).quantize(DEC_PLACES),
                    'volume': Decimal(ticker['ticker']['vol']).quantize(DEC_PLACES),
                    },
            }

def _bitxApiCall(ticker_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=ticker_url, headers=API_REQUEST_HEADERS)).read()
        ticker = json.loads(response)

    return {'ZAR': {'ask': Decimal(ticker['ask']).quantize(DEC_PLACES),
                    'bid': Decimal(ticker['bid']).quantize(DEC_PLACES),
                    'last': Decimal(ticker['last_trade']).quantize(DEC_PLACES),
                    'volume': Decimal(ticker['rolling_24_hour_volume']).quantize(DEC_PLACES),
                    },
            }


def _btctradeApiCall(ticker_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=ticker_url, headers=API_REQUEST_HEADERS)).read()
        ticker = json.loads(response)

    return {'CNY': {'ask': Decimal(ticker['sell']).quantize(DEC_PLACES),
                    'bid': Decimal(ticker['buy']).quantize(DEC_PLACES),
                    'last': Decimal(ticker['last']).quantize(DEC_PLACES),
                    'volume': Decimal(ticker['vol']).quantize(DEC_PLACES),
                    },
            }


def _justcoinApiCall(ticker_url, *args, **kwargs):
    with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
        response = urllib2.urlopen(urllib2.Request(url=ticker_url, headers=API_REQUEST_HEADERS)).read()
        ticker = json.loads(response)

    result = {}
    for currency_data in ticker:
        if currency_data['id'] == 'BTCEUR':
            result['EUR'] = {'ask': Decimal(currency_data['ask']).quantize(DEC_PLACES) if currency_data['ask'] is not None else None,
                             'bid': Decimal(currency_data['bid']).quantize(DEC_PLACES) if currency_data['bid'] is not None else None,
                             'last': Decimal(currency_data['last']).quantize(DEC_PLACES) if currency_data['last'] is not None else None,
                             'volume': Decimal(currency_data['volume']).quantize(DEC_PLACES) if currency_data['volume'] is not None else DEC_PLACES,
                             }
        if currency_data['id'] == 'BTCNOK':
            result['NOK'] = {'ask': Decimal(currency_data['ask']).quantize(DEC_PLACES) if currency_data['ask'] is not None else None,
                             'bid': Decimal(currency_data['bid']).quantize(DEC_PLACES) if currency_data['bid'] is not None else None,
                             'last': Decimal(currency_data['last']).quantize(DEC_PLACES) if currency_data['last'] is not None else None,
                             'volume': Decimal(currency_data['volume']).quantize(DEC_PLACES) if currency_data['volume'] is not None else DEC_PLACES,
                             }

    return result

