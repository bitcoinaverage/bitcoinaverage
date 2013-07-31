from decimal import Decimal

import requests

from bitcoinaverage.config import BITCOIN_CHARTS_API_URL, DEC_PLACES

bitcoincharts_data = None

def fetchBitcoinChartsData():
    global bitcoincharts_data

    bitcoincharts_data = requests.get(BITCOIN_CHARTS_API_URL).json()


def getData(bitcoincharts_symbols):
    global bitcoincharts_data

    if bitcoincharts_data is None:
        fetchBitcoinChartsData()

    return_result = {}

    for api in bitcoincharts_data:
        for currency_code in bitcoincharts_symbols:
            if api['symbol'] == bitcoincharts_symbols[currency_code]:
                return_result[currency_code] = {'ask': Decimal(api['ask']).quantize(DEC_PLACES),
                                                   'bid': Decimal(api['bid']).quantize(DEC_PLACES),
                                                   'last': Decimal(api['close']).quantize(DEC_PLACES),
                                                   'high': Decimal(api['high']).quantize(DEC_PLACES),
                                                   'low': Decimal(api['low']).quantize(DEC_PLACES),
                                                   'volume': Decimal(api['volume']).quantize(DEC_PLACES),
                                                   }

    return return_result