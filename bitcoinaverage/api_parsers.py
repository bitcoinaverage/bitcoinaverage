import requests
from decimal import Decimal

from bitcoinaverage.config import CURRENCY_LIST, DEC_PLACES
from bitcoinaverage.exceptions import NoVolumeException


def mtgoxApiCall(usd_api_url, eur_api_url, gbp_api_url, cad_api_url, rur_api_url, *args, **kwargs):
    usd_result = requests.get(usd_api_url).json()
    eur_result = requests.get(eur_api_url).json()
    gbp_result = requests.get(gbp_api_url).json()
    cad_result = requests.get(cad_api_url).json()
    rur_result = requests.get(rur_api_url).json()

    return {CURRENCY_LIST['USD']: {'ask': Decimal(usd_result['data']['sell']['value']).quantize(DEC_PLACES),
                                   'bid': Decimal(usd_result['data']['buy']['value']).quantize(DEC_PLACES),
                                   'high': Decimal(usd_result['data']['high']['value']).quantize(DEC_PLACES),
                                   'low': Decimal(usd_result['data']['low']['value']).quantize(DEC_PLACES),
                                   'last': Decimal(usd_result['data']['last']['value']).quantize(DEC_PLACES),
                                   'volume': Decimal(usd_result['data']['vol']['value']).quantize(DEC_PLACES),
                                   },
            CURRENCY_LIST['EUR']: {'ask': Decimal(eur_result['data']['sell']['value']).quantize(DEC_PLACES),
                                   'bid': Decimal(eur_result['data']['buy']['value']).quantize(DEC_PLACES),
                                   'high': Decimal(eur_result['data']['high']['value']).quantize(DEC_PLACES),
                                   'low': Decimal(eur_result['data']['low']['value']).quantize(DEC_PLACES),
                                   'last': Decimal(eur_result['data']['last']['value']).quantize(DEC_PLACES),
                                   'volume': Decimal(eur_result['data']['vol']['value']).quantize(DEC_PLACES),
                                   },
            CURRENCY_LIST['GBP']: {'ask': Decimal(gbp_result['data']['sell']['value']).quantize(DEC_PLACES),
                                   'bid': Decimal(gbp_result['data']['buy']['value']).quantize(DEC_PLACES),
                                   'high': Decimal(gbp_result['data']['high']['value']).quantize(DEC_PLACES),
                                   'low': Decimal(gbp_result['data']['low']['value']).quantize(DEC_PLACES),
                                   'last': Decimal(gbp_result['data']['last']['value']).quantize(DEC_PLACES),
                                   'volume': Decimal(gbp_result['data']['vol']['value']).quantize(DEC_PLACES),
                                   },
            CURRENCY_LIST['CAD']: {'ask': Decimal(cad_result['data']['sell']['value']).quantize(DEC_PLACES),
                                   'bid': Decimal(cad_result['data']['buy']['value']).quantize(DEC_PLACES),
                                   'high': Decimal(cad_result['data']['high']['value']).quantize(DEC_PLACES),
                                   'low': Decimal(cad_result['data']['low']['value']).quantize(DEC_PLACES),
                                   'last': Decimal(cad_result['data']['last']['value']).quantize(DEC_PLACES),
                                   'volume': Decimal(cad_result['data']['vol']['value']).quantize(DEC_PLACES),
                                   },
            CURRENCY_LIST['RUR']: {'ask': Decimal(rur_result['data']['sell']['value']).quantize(DEC_PLACES),
                                   'bid': Decimal(rur_result['data']['buy']['value']).quantize(DEC_PLACES),
                                   'high': Decimal(rur_result['data']['high']['value']).quantize(DEC_PLACES),
                                   'low': Decimal(rur_result['data']['low']['value']).quantize(DEC_PLACES),
                                   'last': Decimal(rur_result['data']['last']['value']).quantize(DEC_PLACES),
                                   'volume': Decimal(rur_result['data']['vol']['value']).quantize(DEC_PLACES),
                                   },
           }

def bitstampApiCall(api_url, *args, **kwargs):
    result = requests.get(api_url).json()

    return {CURRENCY_LIST['USD']: {'ask': Decimal(result['ask']).quantize(DEC_PLACES),
                                   'bid': Decimal(result['bid']).quantize(DEC_PLACES),
                                   'high': Decimal(result['high']).quantize(DEC_PLACES),
                                   'low': Decimal(result['low']).quantize(DEC_PLACES),
                                   'last': Decimal(result['last']).quantize(DEC_PLACES),
                                   'volume': Decimal(result['volume']).quantize(DEC_PLACES),
                                   }}

def campbxApiCall(api_url, *args, **kwargs):
    result = requests.get(api_url).json()

    #no volume provided
    # return_data = {CURRENCY_LIST['USD']: {'ask': Decimal(result['Best Ask']).quantize(DEC_PLACES),
    #                                'bid': Decimal(result['Best Bid']).quantize(DEC_PLACES),
    #                                'last': Decimal(result['Last Trade']).quantize(DEC_PLACES),
    #                                }}

    raise NoVolumeException


def btceApiCall(usd_api_url, eur_api_url, rur_api_url, *args, **kwargs):
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

    return {CURRENCY_LIST['USD']: {'ask': Decimal(usd_result['ticker']['sell']).quantize(DEC_PLACES),
                                   'bid': Decimal(usd_result['ticker']['buy']).quantize(DEC_PLACES),
                                   'high': Decimal(usd_result['ticker']['high']).quantize(DEC_PLACES),
                                   'low': Decimal(usd_result['ticker']['low']).quantize(DEC_PLACES),
                                   'last': Decimal(usd_result['ticker']['last']).quantize(DEC_PLACES),
                                   'avg': Decimal(usd_result['ticker']['avg']).quantize(DEC_PLACES),
                                   'volume': Decimal(usd_result['ticker']['vol_cur']).quantize(DEC_PLACES),
                                   },
            CURRENCY_LIST['EUR']: {'ask': Decimal(eur_result['ticker']['sell']).quantize(DEC_PLACES),
                                   'bid': Decimal(eur_result['ticker']['buy']).quantize(DEC_PLACES),
                                   'high': Decimal(eur_result['ticker']['high']).quantize(DEC_PLACES),
                                   'low': Decimal(eur_result['ticker']['low']).quantize(DEC_PLACES),
                                   'last': Decimal(eur_result['ticker']['last']).quantize(DEC_PLACES),
                                   'avg': Decimal(eur_result['ticker']['avg']).quantize(DEC_PLACES),
                                   'volume': Decimal(eur_result['ticker']['vol_cur']).quantize(DEC_PLACES),
                                   },
            CURRENCY_LIST['RUR']: {'ask': Decimal(rur_result['ticker']['sell']).quantize(DEC_PLACES),
                                   'bid': Decimal(rur_result['ticker']['buy']).quantize(DEC_PLACES),
                                   'high': Decimal(rur_result['ticker']['high']).quantize(DEC_PLACES),
                                   'low': Decimal(rur_result['ticker']['low']).quantize(DEC_PLACES),
                                   'last': Decimal(rur_result['ticker']['last']).quantize(DEC_PLACES),
                                   'avg': Decimal(rur_result['ticker']['avg']).quantize(DEC_PLACES),
                                   'volume': Decimal(rur_result['ticker']['vol_cur']).quantize(DEC_PLACES),
                                   }}

def bitcurexApiCall(eur_api_url, *args, **kwargs):
    result = requests.get(eur_api_url).json()


    return {CURRENCY_LIST['EUR']: {'ask': Decimal(result['sell']).quantize(DEC_PLACES),
                                   'bid': Decimal(result['buy']).quantize(DEC_PLACES),
                                   'high': Decimal(result['high']).quantize(DEC_PLACES),
                                   'low': Decimal(result['low']).quantize(DEC_PLACES),
                                   'last': Decimal(result['last']).quantize(DEC_PLACES),
                                   'avg': Decimal(result['avg']).quantize(DEC_PLACES),
                                   'volume': Decimal(result['vol']).quantize(DEC_PLACES),
                                    }}

def vircurexApiCall(usd_api_url, eur_api_url, *args, **kwargs):
    usd_result = requests.get(usd_api_url).json()
    eur_result = requests.get(eur_api_url).json()

    return {CURRENCY_LIST['USD']: {'ask': Decimal(usd_result['lowest_ask']).quantize(DEC_PLACES),
                                   'bid': Decimal(usd_result['highest_bid']).quantize(DEC_PLACES),
                                   'last': Decimal(usd_result['last_trade']).quantize(DEC_PLACES),
                                   'volume': Decimal(usd_result['volume']).quantize(DEC_PLACES),
                                    },
            CURRENCY_LIST['EUR']: {'ask': Decimal(eur_result['lowest_ask']).quantize(DEC_PLACES),
                                   'bid': Decimal(eur_result['highest_bid']).quantize(DEC_PLACES),
                                   'last': Decimal(eur_result['last_trade']).quantize(DEC_PLACES),
                                   'volume': Decimal(eur_result['volume']).quantize(DEC_PLACES),
                                    },
            }
