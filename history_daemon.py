#!/usr/bin/python2.7
import json
import os
import sys
from time import strptime

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)


import time
import requests
import datetime
from email import utils

import bitcoinaverage as ba
from bitcoinaverage.config import HISTORY_QUERY_FREQUENCY, CURRENCY_LIST
from bitcoinaverage.helpers import write_log


if ba.server.PROJECT_PATH == '':
    ba.server.PROJECT_PATH = include_path
if ba.server.LOG_PATH == '':
    ba.server.LOG_PATH = os.path.join(ba.server.PROJECT_PATH, 'runtime', 'app.log')
if ba.server.HISTORY_DOCUMENT_ROOT == '':
    ba.server.HISTORY_DOCUMENT_ROOT = os.path.join(ba.server.PROJECT_PATH, 'history')

write_log('script started', 'LOG')

while True:
    start_time = int(time.time())

    ticker_url = ba.server.API_INDEX_URL+'ticker/all'
    current_data_all = requests.get(ticker_url, headers=ba.config.API_REQUEST_HEADERS).json()

    current_data_datetime = current_data_all['timestamp']
    current_data_datetime = current_data_datetime[:-6] #prior to python 3.2 strptime doesnt work properly with numeric timezone offsets.
    current_data_datetime = datetime.datetime.strptime(current_data_datetime, '%a, %d %b %Y %H:%M:%S')
    current_data_timestamp = int((current_data_datetime - datetime.datetime(1970, 1, 1)).total_seconds())

    current_data_last = {}
    for currency_code in current_data_all:
        if currency_code in CURRENCY_LIST:
            current_data_last[currency_code] = current_data_all[currency_code]['last']

    current_data_year = str(current_data_datetime.year)
    current_data_month = str(current_data_datetime.month).rjust(2, '0')
    current_data_day = str(current_data_datetime.day).rjust(2, '0')
    current_data_history_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, current_data_year, current_data_month)
    if not os.path.exists(current_data_history_path):
        os.makedirs(current_data_history_path)

    with open(os.path.join(current_data_history_path, current_data_day), 'a') as history_file:
        pass  #to make sure file exists, as r+ doesnt create it

    with open(os.path.join(current_data_history_path, current_data_day), 'r') as history_file:
        history_data = history_file.read()
        try:
            history_data = json.loads(history_data)
        except(ValueError):
            history_data = {}
        history_data[current_data_timestamp] = current_data_last

    with open(os.path.join(current_data_history_path, current_data_day), 'w') as history_file:
        history_file.write(json.dumps(history_data, indent=2, sort_keys=True, separators=(',', ': ')))

    timestamp = utils.formatdate(time.time())
    cycle_time = int(time.time())-start_time
    sleep_time = max(0, HISTORY_QUERY_FREQUENCY-cycle_time)
    print '%s, sleeping %ss' % (timestamp, str(sleep_time))

    time.sleep(sleep_time)
