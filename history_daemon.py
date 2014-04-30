#!/usr/bin/python2.7
import os
import sys

import time
import requests
import simplejson
import json
import datetime
import email
import logging

import bitcoinaverage as ba
from bitcoinaverage.config import HISTORY_QUERY_FREQUENCY, CURRENCY_LIST
from bitcoinaverage import history_writers

logger = logging.getLogger("history_daemon")
logger.info("script started")


for currency_code in CURRENCY_LIST:
    if not os.path.exists(os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code)):
        os.makedirs(os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code))

while True:
    ticker_url = ba.server.API_INDEX_URL+'all'
    fiat_data_url = ba.server.API_INDEX_URL+'fiat_data'
    try:
        current_data_all = requests.get(ticker_url, headers=ba.config.API_REQUEST_HEADERS).json()
        fiat_data_all = requests.get(fiat_data_url, headers=ba.config.API_REQUEST_HEADERS).json()
    except (simplejson.decoder.JSONDecodeError, requests.exceptions.ConnectionError), err:
        logger.warning("can not get API data: {0}".format(str(err)))
        time.sleep(10)
        continue

    current_data_datetime = current_data_all['timestamp']
    current_data_datetime = current_data_datetime[:-6] #prior to python 3.2 strptime doesnt work properly with numeric timezone offsets.
    current_data_datetime = datetime.datetime.strptime(current_data_datetime, '%a, %d %b %Y %H:%M:%S')
    current_data_timestamp = int((current_data_datetime - datetime.datetime(1970, 1, 1)).total_seconds())

    for currency_code in CURRENCY_LIST:
        try:
            history_writers.write_24h_csv(currency_code, current_data_all[currency_code]['averages'], current_data_timestamp)
            history_writers.write_1mon_csv(currency_code, current_data_timestamp)
            history_writers.write_forever_csv(currency_code, current_data_all[currency_code]['averages']['total_vol'], current_data_timestamp)
            history_writers.write_volumes_csv(currency_code, current_data_all[currency_code], current_data_timestamp)

            history_writers.write_24h_global_average_csv(fiat_data_all, current_data_all,  currency_code, current_data_timestamp)
            history_writers.write_24h_global_average_short_csv(current_data_all,  currency_code, current_data_timestamp)
        except KeyError, err:
            logger.warning(str(err))

    current_time = time.time()
    timestamp = email.utils.formatdate(current_time)
    sleep_time = HISTORY_QUERY_FREQUENCY - (current_time % HISTORY_QUERY_FREQUENCY)
    sleep_time = min(HISTORY_QUERY_FREQUENCY, sleep_time)

    logger.info("{0}, sleeping {1}s - history daemon".format(timestamp, str(sleep_time)))

    time.sleep(sleep_time)


