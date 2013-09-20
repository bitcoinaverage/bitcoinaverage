from decimal import Decimal
import os
import time
import json
from email import utils
import requests

import bitcoinaverage as ba


def write_log(log_string, message_type='ERROR'):
    timestamp = utils.formatdate(time.time())

    with open(ba.server.LOG_PATH, 'a') as log_file:
        log_string = '%s; %s: %s' % (timestamp, message_type, log_string)
        print log_string
        log_file.write(log_string+'\n')


def write_js_config():
    global ba

    js_config_template = """
var config = {'apiIndexUrl': $API_INDEX_URL,
              'apiIndexUrlNoGox': $API_INDEX_NOGOX_URL,
              'apiHistoryIndexUrl': $API_HISTORY_INDEX_URL,
              'refreshRate': $refreshRate,
              'currencyOrder': $currencyOrder,
              'legendSlots': 20,
              'majorCurrencies': 6
                };
                    """
    config_string = js_config_template
    config_string = config_string.replace('$API_INDEX_URL', '"%s"' % ba.server.API_INDEX_URL)
    config_string = config_string.replace('$API_INDEX_NOGOX_URL', '"%s"' % ba.server.API_INDEX_URL_NOGOX)
    config_string = config_string.replace('$API_HISTORY_INDEX_URL', '"%s"' % ba.server.API_INDEX_URL_HISTORY)

    config_string = config_string.replace('$refreshRate', str(ba.config.FRONTEND_QUERY_FREQUENCY*1000)) #JS requires value in milliseconds
    config_string = config_string.replace('$currencyOrder', json.dumps(ba.config.CURRENCY_LIST))

    with open(os.path.join(ba.server.WWW_DOCUMENT_ROOT, 'config.js'), 'w') as config_file:
        config_file.write(config_string)


def write_fiat_rates_config():
    global ba
    js_config_template = "var fiatCurrencies = $FIAT_CURRENCIES_RATES;"

    google_api_url_template = 'http://www.google.com/ig/calculator?hl=en&q=1USD%3D%3F'

    rate_list = {}

    for currency in ba.config.CURRENCY_LIST:
        api_url = google_api_url_template + currency
        result = requests.get(api_url, headers=ba.config.API_REQUEST_HEADERS).text
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
        try:
            rate = float(rate)
        except ValueError:
            return
        rate = Decimal(rate).quantize(ba.config.DEC_PLACES)
        rate_list[currency] = str(rate)

    config_string = js_config_template
    config_string = config_string.replace('$FIAT_CURRENCIES_RATES', json.dumps(rate_list))

    with open(os.path.join(ba.server.WWW_DOCUMENT_ROOT, 'fiat_rates.js'), 'w') as fiat_exchange_config_file:
        fiat_exchange_config_file.write(config_string)


def write_html_currency_pages():
    global ba

    template_file_path = os.path.join(ba.server.WWW_DOCUMENT_ROOT, '_currency_page_template.htm')
    if not os.path.exists(template_file_path):
        ba.helpers.write_log('currency HTML template file missing', 'ERROR')

    with open(template_file_path, 'r') as template_file:
        template = template_file.read()

    api_all_url = '%sticker/all' % ba.server.API_INDEX_URL
    all_rates = requests.get(api_all_url, headers=ba.config.API_REQUEST_HEADERS).json()

    if not os.path.exists(os.path.join(ba.server.WWW_DOCUMENT_ROOT, ba.config.CURRENCY_DUMMY_PAGES_SUBFOLDER_NAME)):
        os.makedirs(os.path.join(ba.server.WWW_DOCUMENT_ROOT, ba.config.CURRENCY_DUMMY_PAGES_SUBFOLDER_NAME))

    for currency_code in ba.config.CURRENCY_LIST:
        currency_rate = all_rates[currency_code]['last']
        currency_page_contents = template
        currency_page_contents = currency_page_contents.replace('$RATE$', str(Decimal(currency_rate).quantize(ba.config.DEC_PLACES)))
        currency_page_contents = currency_page_contents.replace('$CURRENCY_NAME$', currency_code)

        with open(os.path.join(ba.server.WWW_DOCUMENT_ROOT,
                               ba.config.CURRENCY_DUMMY_PAGES_SUBFOLDER_NAME,
                               ('%s.htm' % currency_code.lower())), 'w') as currency_page_file:
            currency_page_file.write(currency_page_contents)



def write_sitemap():
    pass