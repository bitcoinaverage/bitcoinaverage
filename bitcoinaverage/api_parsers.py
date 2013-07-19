import requests

from bitcoinaverage.config import CURRENCY_LIST

#@TODO all values should be Decimal

def mtgoxApiCall(usd_api_url, eur_api_url, gbp_api_url, cad_api_url, rur_api_url, *args, **kwargs):
    usd_result = requests.get(usd_api_url).json()
    eur_result = requests.get(eur_api_url).json()
    gbp_result = requests.get(gbp_api_url).json()
    cad_result = requests.get(cad_api_url).json()
    rur_result = requests.get(rur_api_url).json()

    return {CURRENCY_LIST['USD']: {'ask': float(usd_result['data']['buy']['value']),
                                   'bid': float(usd_result['data']['sell']['value']),
                                   'high': float(usd_result['data']['high']['value']),
                                   'low': float(usd_result['data']['low']['value']),
                                   'last': float(usd_result['data']['last']['value']),
                                   'volume': float(usd_result['data']['vol']['value']),
                                   },
           CURRENCY_LIST['EUR']: { 'ask': float(eur_result['data']['buy']['value']),
                                   'bid': float(eur_result['data']['sell']['value']),
                                   'high': float(eur_result['data']['high']['value']),
                                   'low': float(eur_result['data']['low']['value']),
                                   'last': float(eur_result['data']['last']['value']),
                                   'volume': float(eur_result['data']['vol']['value']),
                                   },
           CURRENCY_LIST['GBP']: { 'ask': float(gbp_result['data']['buy']['value']),
                                   'bid': float(gbp_result['data']['sell']['value']),
                                   'high': float(gbp_result['data']['high']['value']),
                                   'low': float(gbp_result['data']['low']['value']),
                                   'last': float(gbp_result['data']['last']['value']),
                                   'volume': float(gbp_result['data']['vol']['value']),
                                   },
           CURRENCY_LIST['CAD']: { 'ask': float(cad_result['data']['buy']['value']),
                                   'bid': float(cad_result['data']['sell']['value']),
                                   'high': float(cad_result['data']['high']['value']),
                                   'low': float(cad_result['data']['low']['value']),
                                   'last': float(cad_result['data']['last']['value']),
                                   'volume': float(cad_result['data']['vol']['value']),
                                   },
           CURRENCY_LIST['RUR']: { 'ask': float(rur_result['data']['buy']['value']),
                                   'bid': float(rur_result['data']['sell']['value']),
                                   'high': float(rur_result['data']['high']['value']),
                                   'low': float(rur_result['data']['low']['value']),
                                   'last': float(rur_result['data']['last']['value']),
                                   'volume': float(rur_result['data']['vol']['value']),
                                   },
           }

def bitstampApiCall(api_url, *args, **kwargs):
    result = requests.get(api_url).json()

    return {CURRENCY_LIST['USD']: {'ask': float(result['ask']),
                                   'bid': float(result['bid']),
                                   'high': float(result['high']),
                                   'low': float(result['low']),
                                   'last': float(result['last']),
                                   'volume': float(result['volume']),
                                   }}

def campbxApiCall(api_url, *args, **kwargs):
    result = requests.get(api_url).json()

    return {CURRENCY_LIST['USD']: {'ask': float(result['Best Ask']),
                                   'bid': float(result['Best Bid']),
                                   'last': float(result['Last Trade']),
                                   }}



def btceApiCall(usd_api_url, eur_api_url, rur_api_url, *args, **kwargs):
    usd_result = requests.get(usd_api_url).json()
    eur_result = requests.get(eur_api_url).json()
    rur_result = requests.get(rur_api_url).json()

    return {CURRENCY_LIST['USD']: {'ask': float(usd_result['ticker']['buy']),
                                   'bid': float(usd_result['ticker']['sell']),
                                   'high': float(usd_result['ticker']['high']),
                                   'low': float(usd_result['ticker']['low']),
                                   'last': float(usd_result['ticker']['last']),
                                   'avg': float(usd_result['ticker']['avg']),
                                   'volume': float(usd_result['ticker']['vol_cur']),
                                   },
            CURRENCY_LIST['EUR']: {'ask': float(eur_result['ticker']['buy']),
                                   'bid': float(eur_result['ticker']['sell']),
                                   'high': float(eur_result['ticker']['high']),
                                   'low': float(eur_result['ticker']['low']),
                                   'last': float(eur_result['ticker']['last']),
                                   'avg': float(eur_result['ticker']['avg']),
                                   'volume': float(eur_result['ticker']['vol_cur']),
                                   },
            CURRENCY_LIST['RUR']: {'ask': float(rur_result['ticker']['buy']),
                                   'bid': float(rur_result['ticker']['sell']),
                                   'high': float(rur_result['ticker']['high']),
                                   'low': float(rur_result['ticker']['low']),
                                   'last': float(rur_result['ticker']['last']),
                                   'avg': float(rur_result['ticker']['avg']),
                                   'volume': float(rur_result['ticker']['vol_cur']),
                                   }}

