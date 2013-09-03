from decimal import Decimal
import os
import time
import json
from email import utils
import requests

import bitcoinaverage as ba

def write_config():
    global ba

    js_config_template = """
var config = {'apiIndexUrl': $API_INDEX_URL,
              'apiIndexUrlNoGox': $API_INDEX_NOGOX_URL,
              'apiHistoryIndexUrl': $API_HISTORY_INDEX_NOGOX_URL,
              'refreshRate': $refreshRate,
              'currencyOrder': $currencyOrder
                };
                    """
    config_string = js_config_template
    config_string = config_string.replace('$API_INDEX_URL', '"%s"' % ba.server.API_INDEX_URL)
    config_string = config_string.replace('$API_INDEX_NOGOX_URL', '"%s"' % ba.server.API_INDEX_URL_NOGOX)
    config_string = config_string.replace('$API_HISTORY_INDEX_NOGOX_URL', '"%s"' % ba.server.API_INDEX_URL_NOGOX)

    config_string = config_string.replace('$refreshRate', str(ba.config.FRONTEND_QUERY_FREQUENCY*1000)) #JS requires value in milliseconds
    config_string = config_string.replace('$currencyOrder', json.dumps(ba.config.CURRENCY_LIST))

    with open(os.path.join(ba.server.WWW_DOCUMENT_ROOT, 'config.js'), 'w') as config_file:
        config_file.write(config_string)


def write_log(log_string, message_type='ERROR'):
    timestamp = utils.formatdate(time.time())

    with open(ba.server.LOG_PATH, 'a') as log_file:
        log_string = '%s; %s: %s' % (timestamp, message_type, log_string)
        print log_string
        log_file.write(log_string+'\n')


def write_fiat_rates_config():
    global ba
    js_config_template = "var fiatCurrencies = $FIAT_CURRENCIES_RATES;"

    google_api_url_template = 'http://www.google.com/ig/calculator?hl=en&q=1USD%3D%3F'

    rate_list = {}

    for currency in ba.config.CURRENCY_LIST:
        api_url = google_api_url_template + currency
        result = requests.get(api_url, headers=ba.config.API_REQUEST_HEADERS).text
        ##{lhs: "1 U.S. dollar",rhs: "33.1818031 Russian rubles",error: "",icc: true}
        result = result.replace('lhs', '"lhs"')
        result = result.replace('rhs', '"rhs"')
        result = result.replace('error', '"error"')
        result = result.replace('icc', '"icc"')
        result = json.loads(result)
        rate_string = result['rhs']
        rate = ''
        for c in rate_string:
            if c == ' ':
                break
            else:
                rate = rate + c
        rate = Decimal(rate).quantize(ba.config.DEC_PLACES)
        rate_list[currency] = str(rate)

    config_string = js_config_template
    config_string = config_string.replace('$FIAT_CURRENCIES_RATES', json.dumps(rate_list))

    with open(os.path.join(ba.server.WWW_DOCUMENT_ROOT, 'fiat_rates.js'), 'w') as fiat_exchange_config_file:
        fiat_exchange_config_file.write(config_string)
