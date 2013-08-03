import time
import requests
from decimal import Decimal

import bitcoinaverage
from bitcoinaverage.config import DEC_PLACES, API_QUERY_FREQUENCY

API_QUERY_CACHE = {} #holds last calls to APIs and last received data between calls

def hasAPI(exchange_name):
    return '_%sApiCall' % exchange_name in globals()

def callAPI(exchange_name, exchange_params):
    global API_QUERY_CACHE, API_QUERY_FREQUENCY

    current_timestamp = int(time.time())
    if exchange_name in API_QUERY_FREQUENCY:
        if (exchange_name in API_QUERY_CACHE and
            API_QUERY_CACHE[exchange_name]['last_call_timestamp']+API_QUERY_FREQUENCY[exchange_name] > current_timestamp):
            result = API_QUERY_CACHE[exchange_name]['result']
        else:
            result = globals()['_%sApiCall' % exchange_name](**exchange_params)
            API_QUERY_CACHE[exchange_name] = {'last_call_timestamp': current_timestamp,
                                               'result':result,
                                               }
    else:
        result = globals()['_%sApiCall' % exchange_name](**exchange_params)

    return result

def _mtgoxApiCall(usd_api_url, eur_api_url, gbp_api_url, cad_api_url, pln_api_url, rub_api_url, *args, **kwargs):
    usd_result = requests.get(usd_api_url).json()
    eur_result = requests.get(eur_api_url).json()
    gbp_result = requests.get(gbp_api_url).json()
    cad_result = requests.get(cad_api_url).json()
    pln_result = requests.get(pln_api_url).json()
    rub_result = requests.get(rub_api_url).json()

    return {'USD': {'ask': Decimal(usd_result['data']['sell']['value']).quantize(DEC_PLACES),
                                   'bid': Decimal(usd_result['data']['buy']['value']).quantize(DEC_PLACES),
                                   'high': Decimal(usd_result['data']['high']['value']).quantize(DEC_PLACES),
                                   'low': Decimal(usd_result['data']['low']['value']).quantize(DEC_PLACES),
                                   'last': Decimal(usd_result['data']['last']['value']).quantize(DEC_PLACES),
                                   'volume': Decimal(usd_result['data']['vol']['value']).quantize(DEC_PLACES),
    },
            'EUR': {'ask': Decimal(eur_result['data']['sell']['value']).quantize(DEC_PLACES),
                                   'bid': Decimal(eur_result['data']['buy']['value']).quantize(DEC_PLACES),
                                   'high': Decimal(eur_result['data']['high']['value']).quantize(DEC_PLACES),
                                   'low': Decimal(eur_result['data']['low']['value']).quantize(DEC_PLACES),
                                   'last': Decimal(eur_result['data']['last']['value']).quantize(DEC_PLACES),
                                   'volume': Decimal(eur_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'GBP': {'ask': Decimal(gbp_result['data']['sell']['value']).quantize(DEC_PLACES),
                                   'bid': Decimal(gbp_result['data']['buy']['value']).quantize(DEC_PLACES),
                                   'high': Decimal(gbp_result['data']['high']['value']).quantize(DEC_PLACES),
                                   'low': Decimal(gbp_result['data']['low']['value']).quantize(DEC_PLACES),
                                   'last': Decimal(gbp_result['data']['last']['value']).quantize(DEC_PLACES),
                                   'volume': Decimal(gbp_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'CAD': {'ask': Decimal(cad_result['data']['sell']['value']).quantize(DEC_PLACES),
                                   'bid': Decimal(cad_result['data']['buy']['value']).quantize(DEC_PLACES),
                                   'high': Decimal(cad_result['data']['high']['value']).quantize(DEC_PLACES),
                                   'low': Decimal(cad_result['data']['low']['value']).quantize(DEC_PLACES),
                                   'last': Decimal(cad_result['data']['last']['value']).quantize(DEC_PLACES),
                                   'volume': Decimal(cad_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'PLN': {'ask': Decimal(pln_result['data']['sell']['value']).quantize(DEC_PLACES),
                                   'bid': Decimal(pln_result['data']['buy']['value']).quantize(DEC_PLACES),
                                   'high': Decimal(pln_result['data']['high']['value']).quantize(DEC_PLACES),
                                   'low': Decimal(pln_result['data']['low']['value']).quantize(DEC_PLACES),
                                   'last': Decimal(pln_result['data']['last']['value']).quantize(DEC_PLACES),
                                   'volume': Decimal(pln_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
            'RUB': {'ask': Decimal(rub_result['data']['sell']['value']).quantize(DEC_PLACES),
                                   'bid': Decimal(rub_result['data']['buy']['value']).quantize(DEC_PLACES),
                                   'high': Decimal(rub_result['data']['high']['value']).quantize(DEC_PLACES),
                                   'low': Decimal(rub_result['data']['low']['value']).quantize(DEC_PLACES),
                                   'last': Decimal(rub_result['data']['last']['value']).quantize(DEC_PLACES),
                                   'volume': Decimal(rub_result['data']['vol']['value']).quantize(DEC_PLACES),
            },
    }


def _bitstampApiCall(api_url, *args, **kwargs):
    result = requests.get(api_url).json()

    return {'USD': {'ask': Decimal(result['ask']).quantize(DEC_PLACES),
                                   'bid': Decimal(result['bid']).quantize(DEC_PLACES),
                                   'high': Decimal(result['high']).quantize(DEC_PLACES),
                                   'low': Decimal(result['low']).quantize(DEC_PLACES),
                                   'last': Decimal(result['last']).quantize(DEC_PLACES),
                                   'volume': Decimal(result['volume']).quantize(DEC_PLACES),
    }}

# direct volume calculation gives weird results, bitcoincharts API used for now
#@TODO check with campbx why their API results are incorrect
# def campbxApiCall(api_ticker_url, api_trades_url, *args, **kwargs):
#     ticker_result = requests.get(api_ticker_url).json()
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
#         trades = requests.get(api_trades_url % from_time).json()
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
    usd_result = requests.get(usd_api_url).json()
    eur_result = requests.get(eur_api_url).json()
    rur_result = requests.get(rur_api_url).json()

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
                                   'high': Decimal(usd_result['ticker']['high']).quantize(DEC_PLACES),
                                   'low': Decimal(usd_result['ticker']['low']).quantize(DEC_PLACES),
                                   'last': Decimal(usd_result['ticker']['last']).quantize(DEC_PLACES),
                                   'avg': Decimal(usd_result['ticker']['avg']).quantize(DEC_PLACES),
                                   'volume': Decimal(usd_result['ticker']['vol_cur']).quantize(DEC_PLACES),
    },
            'EUR': {'ask': Decimal(eur_result['ticker']['sell']).quantize(DEC_PLACES),
                                   'bid': Decimal(eur_result['ticker']['buy']).quantize(DEC_PLACES),
                                   'high': Decimal(eur_result['ticker']['high']).quantize(DEC_PLACES),
                                   'low': Decimal(eur_result['ticker']['low']).quantize(DEC_PLACES),
                                   'last': Decimal(eur_result['ticker']['last']).quantize(DEC_PLACES),
                                   'avg': Decimal(eur_result['ticker']['avg']).quantize(DEC_PLACES),
                                   'volume': Decimal(eur_result['ticker']['vol_cur']).quantize(DEC_PLACES),
            },
            'RUB': {'ask': Decimal(rur_result['ticker']['sell']).quantize(DEC_PLACES),
                                   'bid': Decimal(rur_result['ticker']['buy']).quantize(DEC_PLACES),
                                   'high': Decimal(rur_result['ticker']['high']).quantize(DEC_PLACES),
                                   'low': Decimal(rur_result['ticker']['low']).quantize(DEC_PLACES),
                                   'last': Decimal(rur_result['ticker']['last']).quantize(DEC_PLACES),
                                   'avg': Decimal(rur_result['ticker']['avg']).quantize(DEC_PLACES),
                                   'volume': Decimal(rur_result['ticker']['vol_cur']).quantize(DEC_PLACES),
            }}


def _bitcurexApiCall(eur_ticker_url, eur_trades_url, pln_ticker_url, pln_trades_url, *args, **kwargs):
    eur_result = requests.get(eur_ticker_url).json()
    pln_result = requests.get(pln_ticker_url).json()

    last24h_time = int(time.time())-86400  #86400s in 24h
    eur_vol = 0.0
    eur_volume_result = requests.get(eur_trades_url).json()
    for trade in eur_volume_result:
        if trade['date'] > last24h_time:
            eur_vol = eur_vol + float(trade['amount'])

    pln_vol = 0.0
    pln_volume_result = requests.get(pln_trades_url).json()
    for trade in pln_volume_result:
        if trade['date'] > last24h_time:
            pln_vol = pln_vol + float(trade['amount'])

    return {'EUR': {'ask': Decimal(eur_result['sell']).quantize(DEC_PLACES),
                       'bid': Decimal(eur_result['buy']).quantize(DEC_PLACES),
                       'high': Decimal(eur_result['high']).quantize(DEC_PLACES),
                       'low': Decimal(eur_result['low']).quantize(DEC_PLACES),
                       'last': Decimal(eur_result['last']).quantize(DEC_PLACES),
                       'avg': Decimal(eur_result['avg']).quantize(DEC_PLACES),
                       'volume': Decimal(eur_vol).quantize(DEC_PLACES),
                        },
            'PLN': {'ask': Decimal(pln_result['sell']).quantize(DEC_PLACES),
                   'bid': Decimal(pln_result['buy']).quantize(DEC_PLACES),
                   'high': Decimal(pln_result['high']).quantize(DEC_PLACES),
                   'low': Decimal(pln_result['low']).quantize(DEC_PLACES),
                   'last': Decimal(pln_result['last']).quantize(DEC_PLACES),
                   'avg': Decimal(pln_result['avg']).quantize(DEC_PLACES),
                   'volume': Decimal(pln_vol).quantize(DEC_PLACES),
                    },
            }


def _vircurexApiCall(usd_api_url, eur_api_url, *args, **kwargs):
    usd_result = requests.get(usd_api_url).json()
    eur_result = requests.get(eur_api_url).json()

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
    gbp_result = requests.get(gbp_api_url).json()


    average_btc = Decimal(gbp_result['response']['avg_24h'])
    volume_btc = (Decimal(gbp_result['response']['vol_24h']) / average_btc).quantize(DEC_PLACES)

    return {'GBP': {'ask': average_btc.quantize(DEC_PLACES), #bitbargain is an OTC trader, so ask == last
                                   'bid': None, #bitbargain is an OTC trader, so no bids available
                                   'last': average_btc.quantize(DEC_PLACES),
                                   'volume': volume_btc,
                                    },
                }

def _cryptotradeApiCall(usd_api_url, eur_api_url, *args, **kwargs):
    usd_result = requests.get(usd_api_url).json()
    eur_result = requests.get(eur_api_url).json()

    return {'USD': {'ask': Decimal(usd_result['data']['min_ask']).quantize(DEC_PLACES),
                                   'bid': Decimal(usd_result['data']['max_bid']).quantize(DEC_PLACES),
                                   'high': Decimal(usd_result['data']['high']).quantize(DEC_PLACES),
                                   'low': Decimal(usd_result['data']['low']).quantize(DEC_PLACES),
                                   'last': Decimal(usd_result['data']['last']).quantize(DEC_PLACES),
                                   'avg': None,
                                   'volume': Decimal(usd_result['data']['vol_btc']).quantize(DEC_PLACES),
                                    },
            'EUR': {'ask': Decimal(eur_result['data']['min_ask']).quantize(DEC_PLACES),
                                   'bid': Decimal(eur_result['data']['max_bid']).quantize(DEC_PLACES),
                                   'high': Decimal(eur_result['data']['high']).quantize(DEC_PLACES),
                                   'low': Decimal(eur_result['data']['low']).quantize(DEC_PLACES),
                                   'last': Decimal(eur_result['data']['last']).quantize(DEC_PLACES),
                                   'avg': None,
                                   'volume': Decimal(eur_result['data']['vol_btc']).quantize(DEC_PLACES),
                                    },
            }

def _rocktradingApiCall(usd_ticker_url, usd_trades_url, eur_ticker_url, eur_trades_url, *args, **kwargs):
    usd_ticker_result = requests.get(usd_ticker_url, verify=False).json()
    eur_ticker_result = requests.get(eur_ticker_url, verify=False).json()

    last24h_time = int(time.time())-86400  #86400s in 24h

    usd_low = 0.0
    usd_high = 0.0
    usd_last = 0.0
    usd_vol = 0.0

    usd_volume_result = requests.get(usd_trades_url, verify=False).json()
    for trade in usd_volume_result:
        print trade
        exit()
        if trade['date'] > last24h_time:
            if usd_low > float(trade['price']) or usd_low == 0:
                usd_low = float(trade['price'])
            if usd_high < float(trade['price']):
                usd_high = float(trade['price'])
            usd_vol = usd_vol + float(trade['price'])
            usd_last = float(trade['price'])

    eur_low = 0.0
    eur_high = 0.0
    eur_last = 0.0
    eur_vol = 0.0
    eur_volume_result = requests.get(eur_trades_url, verify=False).json()
    for trade in eur_volume_result:
        if trade['date'] > last24h_time:
            if eur_low > float(trade['price']) or eur_low == 0:
                eur_low = float(trade['price'])
            if eur_high < float(trade['price']):
                eur_high = float(trade['price'])
            eur_vol = eur_vol + float(trade['amount'])
            eur_last = float(trade['price'])

    return {'USD': {'ask': Decimal(usd_ticker_result['result'][0]['ask']).quantize(DEC_PLACES),
                                   'bid': Decimal(usd_ticker_result['result'][0]['bid']).quantize(DEC_PLACES),
                                   'high': Decimal(usd_high).quantize(DEC_PLACES),
                                   'low': Decimal(usd_low).quantize(DEC_PLACES),
                                   'last': Decimal(usd_last).quantize(DEC_PLACES),
                                   'avg': None,
                                   'volume': Decimal(usd_vol).quantize(DEC_PLACES),
                                    },
            'EUR': {'ask': Decimal(eur_ticker_result['result'][0]['ask']).quantize(DEC_PLACES),
                                   'bid': Decimal(eur_ticker_result['result'][0]['bid']).quantize(DEC_PLACES),
                                   'high': Decimal(eur_high).quantize(DEC_PLACES),
                                   'low': Decimal(eur_low).quantize(DEC_PLACES),
                                   'last': Decimal(eur_last).quantize(DEC_PLACES),
                                   'avg': None,
                                   'volume': Decimal(eur_vol).quantize(DEC_PLACES),
                                    },
            }
