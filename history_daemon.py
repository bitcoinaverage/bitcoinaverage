#!/usr/bin/python2.7
from decimal import Decimal
import os
import sys

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)


import time
import requests
import datetime
import csv
import json
import email

import bitcoinaverage as ba
from bitcoinaverage.config import HISTORY_QUERY_FREQUENCY, CURRENCY_LIST, DEC_PLACES
from bitcoinaverage.helpers import write_log


if ba.server.PROJECT_PATH == '':
    ba.server.PROJECT_PATH = include_path
if ba.server.LOG_PATH == '':
    ba.server.LOG_PATH = os.path.join(ba.server.PROJECT_PATH, 'runtime', 'app.log')
if ba.server.HISTORY_DOCUMENT_ROOT == '':
    ba.server.HISTORY_DOCUMENT_ROOT = os.path.join(ba.server.PROJECT_PATH, 'api', 'history')

write_log('script started', 'LOG')

def write_24h_csv(currency_code, current_data, last_timestamp):
    if not os.path.exists(os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code)):
        os.makedirs(os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code))

    current_24h_sliding_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, '24h_sliding.csv')

    current_24h_sliding_data = []
    with open(current_24h_sliding_file_path, 'a') as csvfile: #to create file if not exists
        pass

    with open(current_24h_sliding_file_path, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            timestamp = time.mktime(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').timetuple())
            if last_timestamp - timestamp < 86400: #60*60*24
                current_24h_sliding_data.append(row)
    current_24h_sliding_data.append([datetime.datetime.strftime(datetime.datetime.fromtimestamp(last_timestamp), '%Y-%m-%d %H:%M:%S'),
                                     current_data['last']])

    with open(current_24h_sliding_file_path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        for row in current_24h_sliding_data:
            csvwriter.writerow(row)


def write_1mon_csv(currency_code, last_value, last_timestamp):
    current_1h_1mon_sliding_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, '1mon_sliding.csv')

    current_1mon_sliding_data = []
    with open(current_1h_1mon_sliding_file_path, 'a') as csvfile: #to create file if not exists
        pass

    with open(current_1h_1mon_sliding_file_path, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            timestamp = time.mktime(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').timetuple())
            if last_timestamp - timestamp < 2592000: #60*60*24*30
                current_1mon_sliding_data.append(row)

    last_date = 0
    if len(current_1mon_sliding_data) > 0:
        last_date = time.mktime(datetime.datetime.strptime(current_1mon_sliding_data[len(current_1mon_sliding_data)-1][0],
                                                           '%Y-%m-%d %H:%M:%S').timetuple())


    if int(time.time())-last_date > 3600:
        current_24h_sliding_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, '24h_sliding.csv')
        price_high = 0.0
        price_low = 0.0
        price_sum = Decimal(DEC_PLACES)
        index = 0
        with open(current_24h_sliding_file_path, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            for row in csvreader:
                timestamp = time.mktime(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').timetuple())
                if last_timestamp - timestamp < 3600: #60*60*24
                    index = index + 1
                    price = float(row[1])
                    price_sum = price_sum + Decimal(price)
                    if price_high < price:
                        price_high = price
                    if price_low == 0 or price_low > price:
                        price_low = price

        try:
            price_avg = price_sum / Decimal(index)
        except(ZeroDivisionError):
            price_avg = DEC_PLACES

        


    current_1mon_sliding_data.append([datetime.datetime.strftime(datetime.datetime.fromtimestamp(last_timestamp), '%Y-%m-%d %H:%M:%S'), last_value])

    with open(current_24h_sliding_file_path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        for row in current_24h_sliding_data:
            csvwriter.writerow(row)


def write_forever_csv(currency_code, last_value, last_timestamp):
    pass

while True:
    start_time = int(time.time())

    ticker_url = ba.server.API_INDEX_URL+'ticker/all'
    current_data_all = requests.get(ticker_url, headers=ba.config.API_REQUEST_HEADERS).json()
    current_data_datetime = current_data_all['timestamp']
    current_data_datetime = current_data_datetime[:-6] #prior to python 3.2 strptime doesnt work properly with numeric timezone offsets.
    current_data_datetime = datetime.datetime.strptime(current_data_datetime, '%a, %d %b %Y %H:%M:%S')
    current_data_timestamp = int((current_data_datetime - datetime.datetime(1970, 1, 1)).total_seconds())

    for currency_code in current_data_all:
        if currency_code in CURRENCY_LIST:
            if not os.path.exists(os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code)):
                os.makedirs(os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code))
            write_24h_csv(currency_code, current_data_all[currency_code], current_data_timestamp)
            write_1mon_csv(currency_code, current_data_all[currency_code], current_data_timestamp)
            write_forever_csv(currency_code, current_data_all[currency_code], current_data_timestamp)


    timestamp = email.utils.formatdate(time.time())
    cycle_time = int(time.time())-start_time
    sleep_time = max(0, HISTORY_QUERY_FREQUENCY-cycle_time)

    print '%s, sleeping %ss - history daemon' % (timestamp, str(sleep_time))

    time.sleep(sleep_time)


