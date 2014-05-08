from decimal import Decimal
import os
from shutil import copyfile
import time
import json
from email import utils
import datetime
import socket
from lxml import etree
from eventlet.green import urllib2
from eventlet.timeout import Timeout
from eventlet.green import httplib
import simplejson
import hashlib
import gzip

import bitcoinaverage as ba
from bitcoinaverage.config import API_CALL_TIMEOUT_THRESHOLD, API_REQUEST_HEADERS, API_FILES
from bitcoinaverage.server import OPENEXCHANGERATES_APP_ID
from bitcoinaverage.exceptions import CallTimeoutException


def write_js_config():
    global ba

    js_config_template = 'var config = $CONFIG_DATA;'

    exchange_color = lambda name: "#" + hashlib.md5(name.encode()).hexdigest()[:6]

    config_data = {}
    config_data['apiIndexUrl'] = ba.server.API_INDEX_URL
    config_data['apiHistoryIndexUrl'] = ba.server.API_INDEX_URL_HISTORY
    config_data['refreshRate'] = str(ba.config.FRONTEND_QUERY_FREQUENCY*1000) #JS requires value in milliseconds
    config_data['currencyOrder'] = ba.config.CURRENCY_LIST
    config_data['legendSlots'] = ba.config.FRONTEND_LEGEND_SLOTS
    config_data['majorCurrencies'] = ba.config.FRONTEND_MAJOR_CURRENCIES
    config_data['scaleDivizer'] = ba.config.FRONTEND_SCALE_DIVIZER
    config_data['precision'] = ba.config.FRONTEND_PRECISION
    config_data['exchangesColors'] = {ex: exchange_color(ex) for ex in ba.config.EXCHANGE_LIST.keys()}
    config_data['currencySymbols'] = ba.config.FRONTEND_CURRENCY_SYMBOLS
    config_data['apiUsers'] = ba.config.API_USERS
    config_string = js_config_template.replace('$CONFIG_DATA',
            json.dumps(config_data, ensure_ascii=False).encode('utf8'))

    with open(os.path.join(ba.server.WWW_DOCUMENT_ROOT, 'js', 'config.js'), 'w') as config_file:
        config_file.write(config_string)


def write_fiat_rates_config():
    global ba
    js_config_template = "var fiatCurrencies = $FIAT_CURRENCIES_DATA$;"

    currencies_names_URL = 'http://openexchangerates.org/api/currencies.json'
    currencies_rates_URL = 'http://openexchangerates.org/api/latest.json?app_id={app_id}'.format(app_id=OPENEXCHANGERATES_APP_ID)

    currency_data_list = {}

    try:
        with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
            response = urllib2.urlopen(urllib2.Request(url=currencies_names_URL, headers=API_REQUEST_HEADERS)).read()
            currencies_names = json.loads(response)

        with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
            response = urllib2.urlopen(urllib2.Request(url=currencies_rates_URL, headers=API_REQUEST_HEADERS)).read()
            currencies_rates = json.loads(response)
    except (CallTimeoutException,
            socket.error,
            urllib2.URLError,
            httplib.BadStatusLine,
            ValueError):
        return None

    for currency_code in currencies_names:
        try:
            currency_data_list[currency_code] = {'name': currencies_names[currency_code],
                                                 'rate': str(currencies_rates['rates'][currency_code]),
                                                 }
        except (KeyError, TypeError):
            return None

    config_string = js_config_template
    config_string = config_string.replace('$FIAT_CURRENCIES_DATA$', json.dumps(currency_data_list))

    with open(os.path.join(ba.server.WWW_DOCUMENT_ROOT, 'js', 'fiat_data.js'), 'w') as fiat_exchange_config_file:
        fiat_exchange_config_file.write(config_string)

    with open(os.path.join(ba.server.API_DOCUMENT_ROOT, 'fiat_data'), 'w') as fiat_exchange_api_file:
        fiat_exchange_api_file.write(json.dumps(currency_data_list))


def write_html_currency_pages():
    global ba
    today = datetime.datetime.today()

    template_file_path = os.path.join(ba.server.WWW_DOCUMENT_ROOT, '_currency_page_template.htm')
    with open(template_file_path, 'r') as template_file:
        template = template_file.read()

    api_all_url = '{}ticker/all'.format(ba.server.API_INDEX_URL)

    try:
        with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
            response = urllib2.urlopen(urllib2.Request(url=api_all_url, headers=API_REQUEST_HEADERS)).read()
            all_rates = json.loads(response)
    except (CallTimeoutException,
            socket.error,
            urllib2.URLError,
            httplib.BadStatusLine,
            simplejson.decoder.JSONDecodeError):
        return None

    if not os.path.exists(os.path.join(ba.server.WWW_DOCUMENT_ROOT, ba.config.CURRENCY_DUMMY_PAGES_SUBFOLDER_NAME)):
        os.makedirs(os.path.join(ba.server.WWW_DOCUMENT_ROOT, ba.config.CURRENCY_DUMMY_PAGES_SUBFOLDER_NAME))

    for currency_code in ba.config.CURRENCY_LIST:
        currency_rate = all_rates[currency_code]['last']
        currency_page_contents = template
        currency_page_contents = currency_page_contents.replace('$RATE$', str(Decimal(currency_rate).quantize(ba.config.DEC_PLACES)))
        currency_page_contents = currency_page_contents.replace('$CURRENCY_CODE$', currency_code)
        currency_page_contents = currency_page_contents.replace('$GENERATION_DATETIME$', today.strftime('%Y-%m-%dT%H:%M'))

        with open(os.path.join(ba.server.WWW_DOCUMENT_ROOT,
                               ba.config.CURRENCY_DUMMY_PAGES_SUBFOLDER_NAME,
                               ('%s.htm' % currency_code.lower())), 'w') as currency_page_file:
            currency_page_file.write(currency_page_contents)

    template_file_path = os.path.join(ba.server.WWW_DOCUMENT_ROOT, '_charts_page_template.htm')
    with open(template_file_path, 'r') as template_file:
        template = template_file.read()

    if not os.path.exists(os.path.join(ba.server.WWW_DOCUMENT_ROOT, ba.config.CHARTS_DUMMY_PAGES_SUBFOLDER_NAME)):
        os.makedirs(os.path.join(ba.server.WWW_DOCUMENT_ROOT, ba.config.CHARTS_DUMMY_PAGES_SUBFOLDER_NAME))

    index = 0
    for currency_code in ba.config.CURRENCY_LIST:
        currency_rate = all_rates[currency_code]['last']
        chart_page_contents = template
        chart_page_contents = chart_page_contents.replace('$RATE$', str(Decimal(currency_rate).quantize(ba.config.DEC_PLACES)))
        chart_page_contents = chart_page_contents.replace('$CURRENCY_CODE$', currency_code)
        chart_page_contents = chart_page_contents.replace('$GENERATION_DATETIME$', today.strftime('%Y-%m-%dT%H:%M'))
        with open(os.path.join(ba.server.WWW_DOCUMENT_ROOT,
                               ba.config.CHARTS_DUMMY_PAGES_SUBFOLDER_NAME,
                               ('%s.htm' % currency_code.lower())), 'w') as chart_page_file:
            chart_page_file.write(chart_page_contents)


        index = index + 1
        if index == ba.config.FRONTEND_MAJOR_CURRENCIES:
            break


def write_sitemap():
    global ba

    def _sitemap_append_url(url_str, lastmod_date=None, changefreq_str=None, priority_str=None):
        url = etree.Element('url')
        loc = etree.Element('loc')
        loc.text = url_str
        url.append(loc)
        if lastmod_date is not None:
            lastmod = etree.Element('lastmod')
            lastmod.text = lastmod_date.strftime('%Y-%m-%d')
            url.append(lastmod)
        if changefreq_str is not None:
            changefreq = etree.Element('changefreq')
            changefreq.text = changefreq_str
            url.append(changefreq)
        if priority_str is not None:
            priority = etree.Element('priority')
            priority.text = priority_str
            url.append(priority)
        return url

    urlset = etree.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')

    index_url = '%s%s' % (ba.server.FRONTEND_INDEX_URL, 'index.htm')
    today = datetime.datetime.today()
    urlset.append(_sitemap_append_url('%s%s' % (ba.server.FRONTEND_INDEX_URL, 'index.htm'), today, 'hourly', '1.0'))
    urlset.append(_sitemap_append_url('%s%s' % (ba.server.FRONTEND_INDEX_URL, 'faq.htm'), today, 'monthly', '0.5'))
    urlset.append(_sitemap_append_url('%s%s' % (ba.server.FRONTEND_INDEX_URL, 'api.htm'), today, 'monthly', '0.5'))
    urlset.append(_sitemap_append_url('%s%s' % (ba.server.FRONTEND_INDEX_URL, 'blog.htm'), today, 'weekly', '1.0'))
    urlset.append(_sitemap_append_url('%s%s' % (ba.server.FRONTEND_INDEX_URL, 'charts.htm'), today, 'hourly', '0.8'))

    currency_static_seo_pages_dir = os.path.join(ba.server.WWW_DOCUMENT_ROOT, ba.config.CURRENCY_DUMMY_PAGES_SUBFOLDER_NAME)
    for dirname, dirnames, filenames in os.walk(currency_static_seo_pages_dir):
        for filename in filenames:
            urlset.append(_sitemap_append_url('%s%s/%s' % (ba.server.FRONTEND_INDEX_URL,
                                                        ba.config.CURRENCY_DUMMY_PAGES_SUBFOLDER_NAME,
                                                        filename), today, 'hourly', '1.0'))
    charts_static_seo_pages_dir = os.path.join(ba.server.WWW_DOCUMENT_ROOT, ba.config.CHARTS_DUMMY_PAGES_SUBFOLDER_NAME)
    index = 0
    for dirname, dirnames, filenames in os.walk(currency_static_seo_pages_dir):
        for filename in filenames:
            urlset.append(_sitemap_append_url('%s%s/%s' % (ba.server.FRONTEND_INDEX_URL,
                                                        ba.config.CHARTS_DUMMY_PAGES_SUBFOLDER_NAME,
                                                        filename), today, 'hourly', '0.8'))
            index = index + 1
            if index == ba.config.FRONTEND_MAJOR_CURRENCIES:
                break
        break

    xml_sitemap_contents = '<?xml version="1.0" encoding="UTF-8"?>\n' + etree.tostring(urlset, pretty_print=True)
    with open(os.path.join(ba.server.WWW_DOCUMENT_ROOT, 'sitemap.xml'), 'w') as sitemap_file:
        sitemap_file.write(xml_sitemap_contents)


def write_api_index_files():
    def _write_history_index_file(currency_code):
        global ba
        if not os.path.exists(os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code)):
            os.makedirs(os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code))

        current_index_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, ba.config.INDEX_DOCUMENT_NAME)

        index_contents = {}
        index_contents['24h_sliding'] = '%s%s/per_minute_24h_sliding_window.csv' % (ba.server.API_INDEX_URL_HISTORY, currency_code)
        index_contents['monthly_sliding'] = '%s%s/per_hour_monthly_sliding_window.csv' % (ba.server.API_INDEX_URL_HISTORY, currency_code)
        index_contents['all_time'] = '%s%s/per_day_all_time_history.csv' % (ba.server.API_INDEX_URL_HISTORY, currency_code)
        index_contents['volumes'] = '%s%s/volumes.csv' % (ba.server.API_INDEX_URL_HISTORY, currency_code)
        index_contents['global_24h_sliding'] = '%s%s/per_minute_24h_global_average_sliding_window.csv' % (ba.server.API_INDEX_URL_HISTORY, currency_code)

        write_api_file(
            current_index_file_path,
            json.dumps(index_contents, indent=2, sort_keys=True, separators=(',', ': ')))

    global ba

    if not os.path.exists(os.path.join(ba.server.API_DOCUMENT_ROOT, 'favicon.ico')):
        try:
            copyfile(os.path.join(ba.server.WWW_DOCUMENT_ROOT, 'favicon.ico'),
                     os.path.join(ba.server.API_DOCUMENT_ROOT, 'favicon.ico'))
        except IOError:
            pass

    #api root index
    api_index = {}
    api_index['tickers'] = ba.server.API_INDEX_URL + API_FILES['TICKER_PATH']
    api_index['global_tickers'] = ba.server.API_INDEX_URL + API_FILES['GLOBAL_TICKER_PATH']
    api_index['exchanges'] = ba.server.API_INDEX_URL + API_FILES['EXCHANGES_PATH']
    api_index['all'] = ba.server.API_INDEX_URL + API_FILES['ALL_FILE']
    api_index['ignored'] = ba.server.API_INDEX_URL + API_FILES['IGNORED_FILE']
    api_index['history'] = ba.server.API_INDEX_URL_HISTORY
    write_api_file(
        os.path.join(ba.server.API_DOCUMENT_ROOT, ba.config.INDEX_DOCUMENT_NAME),
        json.dumps(api_index, indent=2, sort_keys=True, separators=(',', ': ')))

    #api tickers index
    if not os.path.exists(os.path.join(ba.server.API_DOCUMENT_ROOT, API_FILES['TICKER_PATH'])):
        os.makedirs(os.path.join(ba.server.API_DOCUMENT_ROOT, API_FILES['TICKER_PATH']))

    api_ticker_index = {}
    api_ticker_index['all'] = ba.server.API_INDEX_URL + API_FILES['TICKER_PATH'] + API_FILES['ALL_FILE']
    api_ticker_folder_path = os.path.join(ba.server.API_DOCUMENT_ROOT, API_FILES['TICKER_PATH'])
    for currency_code in ba.config.CURRENCY_LIST:
        api_ticker_index[currency_code] = ba.server.API_INDEX_URL + API_FILES['TICKER_PATH'] + currency_code
        if not os.path.exists(os.path.join(api_ticker_folder_path, currency_code)):
            os.makedirs(os.path.join(api_ticker_folder_path, currency_code))
    write_api_file(
        os.path.join(ba.server.API_DOCUMENT_ROOT, API_FILES['TICKER_PATH'], ba.config.INDEX_DOCUMENT_NAME),
        json.dumps(api_ticker_index, indent=2, sort_keys=True, separators=(',', ': ')))

    #api global tickers index
    if not os.path.exists(os.path.join(ba.server.API_DOCUMENT_ROOT, API_FILES['GLOBAL_TICKER_PATH'])):
        os.makedirs(os.path.join(ba.server.API_DOCUMENT_ROOT, API_FILES['GLOBAL_TICKER_PATH']))

    api_ticker_index = {}
    api_ticker_index['all'] = ba.server.API_INDEX_URL + API_FILES['GLOBAL_TICKER_PATH'] + API_FILES['ALL_FILE']
    api_ticker_folder_path = os.path.join(ba.server.API_DOCUMENT_ROOT, API_FILES['GLOBAL_TICKER_PATH'])

    try:
        fiat_exchange_rates_url = ba.server.API_INDEX_URL + 'fiat_data'
        with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
            result = urllib2.urlopen(urllib2.Request(url=fiat_exchange_rates_url, headers=API_REQUEST_HEADERS)).read()
            fiat_currencies_list = json.loads(result)

        for currency_code in fiat_currencies_list:
            api_ticker_index[currency_code] = ba.server.API_INDEX_URL + API_FILES['GLOBAL_TICKER_PATH'] + currency_code
            if not os.path.exists(os.path.join(api_ticker_folder_path, currency_code)):
                os.makedirs(os.path.join(api_ticker_folder_path, currency_code))
        write_api_file(
            os.path.join(ba.server.API_DOCUMENT_ROOT, API_FILES['GLOBAL_TICKER_PATH'], ba.config.INDEX_DOCUMENT_NAME),
            json.dumps(api_ticker_index, indent=2, sort_keys=True, separators=(',', ': ')))
    except (KeyError,ValueError,socket.error,simplejson.decoder.JSONDecodeError,urllib2.URLError,httplib.BadStatusLine,CallTimeoutException):
        pass

    #api exchanges index
    if not os.path.exists(os.path.join(ba.server.API_DOCUMENT_ROOT, API_FILES['EXCHANGES_PATH'])):
        os.makedirs(os.path.join(ba.server.API_DOCUMENT_ROOT, API_FILES['EXCHANGES_PATH']))

    api_exchanges_index = {}
    api_exchanges_index['all'] = ba.server.API_INDEX_URL + API_FILES['EXCHANGES_PATH'] + API_FILES['ALL_FILE']
    for currency_code in ba.config.CURRENCY_LIST:
        api_exchanges_index[currency_code] = ba.server.API_INDEX_URL + API_FILES['EXCHANGES_PATH'] + currency_code
    write_api_file(
        os.path.join(ba.server.API_DOCUMENT_ROOT, API_FILES['EXCHANGES_PATH'], ba.config.INDEX_DOCUMENT_NAME),
        json.dumps(api_exchanges_index, indent=2, sort_keys=True, separators=(',', ': ')))


    #api history index files
    if not os.path.exists(os.path.join(ba.server.HISTORY_DOCUMENT_ROOT)):
        os.makedirs(os.path.join(ba.server.HISTORY_DOCUMENT_ROOT))

    currency_history_links_list = {}
    for currency_code in ba.config.CURRENCY_LIST:
        _write_history_index_file(currency_code)
        currency_history_links_list[currency_code] = '%s%s/' % (ba.server.API_INDEX_URL_HISTORY, currency_code)

    general_index_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, ba.config.INDEX_DOCUMENT_NAME)
    write_api_file(
        general_index_file_path,
        json.dumps(currency_history_links_list, indent=2, sort_keys=True, separators=(',', ': ')))


def write_api_file(api_file_name, content, compress=True):
    with open(api_file_name, 'w') as api_file:
        api_file.write(content)
    if compress:
        with open(api_file_name, 'rb') as api_file:
            with gzip.open(api_file_name + '.gz', 'wb') as api_gzipped_file:
                api_gzipped_file.writelines(api_file)


def gzip_history_file(history_file_name):
    with open(history_file_name, 'rb') as history_file:
        with gzip.open(history_file_name + '.gz', 'wb') as history_gzipped_file:
            history_gzipped_file.writelines(history_file)
