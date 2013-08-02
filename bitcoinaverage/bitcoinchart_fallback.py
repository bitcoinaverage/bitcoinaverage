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
                value_ask = api['ask'] if api['ask'] is not None else 0.0
                value_bid = api['bid'] if api['bid'] is not None else 0.0
                value_close = api['close'] if api['close'] is not None else 0.0
                value_high = api['high'] if api['high'] is not None else 0.0
                value_low = api['low'] if api['low'] is not None else 0.0
                value_volume = api['volume'] if api['volume'] is not None else 0.0

                return_result[currency_code] = {'ask': Decimal(value_ask).quantize(DEC_PLACES),
                                                   'bid': Decimal(float(value_bid)).quantize(DEC_PLACES),
                                                   'last': Decimal(float(value_close)).quantize(DEC_PLACES),
                                                   'high': Decimal(float(value_high)).quantize(DEC_PLACES),
                                                   'low': Decimal(float(value_low)).quantize(DEC_PLACES),
                                                   'volume': Decimal(float(value_volume)).quantize(DEC_PLACES),
                                                   }

    return return_result