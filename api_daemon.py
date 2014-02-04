#!/usr/bin/python2.7
import os
import sys

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)


import time
from email import utils

import bitcoinaverage as ba
import bitcoinaverage.server
from bitcoinaverage import api_parsers
from bitcoinaverage.config import API_QUERY_FREQUENCY, FIAT_RATES_QUERY_FREQUENCY
import bitcoinaverage.helpers as helpers
from bitcoinaverage.api_calculations import calculateTotalVolumes, calculateRelativeVolumes, calculateAverageRates, formatDataForAPI, writeAPIFiles, createNogoxApi, calculateAllGlobalAverages

if ba.server.PROJECT_PATH == '':
    ba.server.PROJECT_PATH = include_path
if ba.server.LOG_PATH == '':
    ba.server.LOG_PATH = os.path.join(ba.server.PROJECT_PATH, 'runtime', 'app.log')
if ba.server.API_DOCUMENT_ROOT == '':
    ba.server.API_DOCUMENT_ROOT = os.path.join(ba.server.PROJECT_PATH, 'api')
    ba.server.API_DOCUMENT_ROOT_NOGOX = os.path.join(ba.server.API_DOCUMENT_ROOT, 'no-mtgox')
if ba.server.WWW_DOCUMENT_ROOT == '':
    ba.server.WWW_DOCUMENT_ROOT = os.path.join(ba.server.PROJECT_PATH, 'www')
if ba.server.HISTORY_DOCUMENT_ROOT == '':
    ba.server.HISTORY_DOCUMENT_ROOT = os.path.join(ba.server.PROJECT_PATH, 'api', 'history')

helpers.write_log('script started', 'LOG')
helpers.write_js_config()
helpers.write_fiat_rates_config()
last_fiat_exchange_rate_update = time.time()
helpers.write_api_index_files()

while True:
    if last_fiat_exchange_rate_update < int(time.time())-FIAT_RATES_QUERY_FREQUENCY:
        helpers.write_fiat_rates_config()

    start_time = int(time.time())

    exchanges_rates, exchanges_ignored = ba.api_parsers.callAll()

    total_currency_volumes, total_currency_volumes_ask, total_currency_volumes_bid = calculateTotalVolumes(exchanges_rates)
    calculated_volumes = calculateRelativeVolumes(exchanges_rates,
                                                  total_currency_volumes,
                                                  total_currency_volumes_ask,
                                                  total_currency_volumes_bid)
    calculated_average_rates = calculateAverageRates(exchanges_rates, calculated_volumes)

    calculated_global_average_rates, calculated_global_volume_percents = calculateAllGlobalAverages(calculated_average_rates,
                                                                                                    total_currency_volumes)

    (calculated_average_rates_formatted,
     calculated_volumes_formatted,
     calculated_global_average_rates_formatted) = formatDataForAPI(calculated_average_rates,
                                                                   calculated_volumes,
                                                                   total_currency_volumes,
                                                                   calculated_global_average_rates,
                                                                   calculated_global_volume_percents)

    human_timestamp = utils.formatdate(time.time())
    writeAPIFiles(ba.server.API_DOCUMENT_ROOT,
                  human_timestamp,
                  calculated_average_rates_formatted,
                  calculated_volumes_formatted,
                  calculated_global_average_rates_formatted,
                  exchanges_ignored)

    createNogoxApi(human_timestamp, exchanges_rates, exchanges_ignored)


    if last_fiat_exchange_rate_update < int(time.time())-FIAT_RATES_QUERY_FREQUENCY:
        helpers.write_html_currency_pages()
        helpers.write_sitemap()
        last_fiat_exchange_rate_update = int(time.time())

    cycle_time = int(time.time())-start_time
    sleep_time = max(0, API_QUERY_FREQUENCY['default']-cycle_time)
    print '{timestamp}, spent {spent}s, sleeping {sleep}s - api daemon'.format(timestamp=human_timestamp,
                                                                               spent=cycle_time,
                                                                               sleep=str(sleep_time))

    time.sleep(sleep_time)
