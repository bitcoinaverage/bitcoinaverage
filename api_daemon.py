#!/usr/bin/python2.7
import os
import sys
import time
from email import utils

import redis
import simplejson as json

import bitcoinaverage as ba
import bitcoinaverage.server
from bitcoinaverage import api_custom_writers
from bitcoinaverage.config import API_QUERY_FREQUENCY, FIAT_RATES_QUERY_FREQUENCY
import bitcoinaverage.helpers as helpers
from bitcoinaverage.api_calculations import calculateTotalVolumes, calculateRelativeVolumes, calculateAverageRates, formatDataForAPI, writeAPIFiles, calculateAllGlobalAverages

helpers.write_log('script started', 'LOG')
helpers.write_js_config()
helpers.write_fiat_rates_config()
last_fiat_exchange_rate_update = time.time()
helpers.write_api_index_files()

red = redis.StrictRedis(host="localhost", port=6379, db=0)

while True:
    if last_fiat_exchange_rate_update < int(time.time())-FIAT_RATES_QUERY_FREQUENCY:
        helpers.write_fiat_rates_config()

    start_time = int(time.time())

    if not red.exists("ba:exchanges"):
        time.sleep(API_QUERY_FREQUENCY['default'])
        continue
    exchanges_rates = []
    exchanges_ignored = {}
    for exchange_data in red.hgetall("ba:exchanges").itervalues():
        exchanges_rates.append(json.loads(exchange_data, use_decimal=True))
    for exchange_name, exchange_ignore_reason in red.hgetall("ba:exchanges_ignored").iteritems():
        exchanges_ignored[exchange_name] = exchange_ignore_reason

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

    api_custom_writers.createCustomAPIs(ba.server.API_DOCUMENT_ROOT,
                                        human_timestamp,
                                        calculated_average_rates_formatted,
                                        calculated_volumes_formatted,
                                        calculated_global_average_rates_formatted,
                                        exchanges_ignored)


    if last_fiat_exchange_rate_update < int(time.time())-FIAT_RATES_QUERY_FREQUENCY:
        helpers.write_sitemap()
        last_fiat_exchange_rate_update = int(time.time())

    cycle_time = int(time.time())-start_time
    sleep_time = max(0, API_QUERY_FREQUENCY['default']-cycle_time)
    helpers.write_log("{timestamp}, spent {spent}s, sleeping {sleep}s - api daemon".format(
        timestamp=human_timestamp,
        spent=cycle_time,
        sleep=str(sleep_time)), "LOG")

    time.sleep(sleep_time)
