import os
import time
import datetime
from decimal import Decimal
import csv
import json

import bitcoinaverage as ba
from bitcoinaverage.config import DEC_PLACES

def write_default(currency_code):
    current_default_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, ba.config.INDEX_DOCUMENT_NAME)
    if not os.path.exists(os.path.join(current_default_file_path)) or os.path.getsize(current_default_file_path) == 0:
        with open(current_default_file_path, 'wb') as default_file:
            default_contents = {}
            default_contents['24h_sliding'] = ba.server.API_INDEX_URL_HISTORY+'%s/24h_sliding.csv' % currency_code
            default_contents['1mon_sliding'] = ba.server.API_INDEX_URL_HISTORY+'%s/1mon_sliding.csv' % currency_code
            default_contents['forever'] = ba.server.API_INDEX_URL_HISTORY+'%s/forever.csv' % currency_code
            default_contents['volumes'] = ba.server.API_INDEX_URL_HISTORY+'%s/volumes.csv' % currency_code
            default_file.write(json.dumps(default_contents))

def write_24h_csv(currency_code, current_data, last_timestamp):
    current_24h_sliding_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, '24h_sliding.csv')

    current_24h_sliding_data = []
    with open(current_24h_sliding_file_path, 'a') as csvfile: #to create file if not exists
        pass

    with open(current_24h_sliding_file_path, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        header_passed = False
        for row in csvreader:
            if not header_passed:
                header_passed = True
                continue
            timestamp = time.mktime(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').timetuple())
            if last_timestamp - timestamp < 86400: #60*60*24
                current_24h_sliding_data.append(row)

    last_recorded_timestamp = 0
    if len(current_24h_sliding_data) > 0:
        last_recorded_timestamp = time.mktime(datetime.datetime.strptime(current_24h_sliding_data[len(current_24h_sliding_data)-1][0],
                                                           '%Y-%m-%d %H:%M:%S').timetuple())

    if last_timestamp - last_recorded_timestamp > 60:
        current_24h_sliding_data.append([datetime.datetime.strftime(datetime.datetime.fromtimestamp(last_timestamp), '%Y-%m-%d %H:%M:%S'),
                                         current_data['last']])

    with open(current_24h_sliding_file_path, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(['datetime','average'])
        for row in current_24h_sliding_data:
            csvwriter.writerow(row)


def write_1mon_csv(currency_code, last_timestamp):
    current_1h_1mon_sliding_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, '1mon_sliding.csv')

    current_1mon_sliding_data = []
    with open(current_1h_1mon_sliding_file_path, 'a') as csvfile: #to create file if not exists
        pass

    with open(current_1h_1mon_sliding_file_path, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', )
        header_passed = False
        for row in csvreader:
            if not header_passed:
                header_passed = True
                continue
            timestamp = time.mktime(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').timetuple())
            if last_timestamp - timestamp < 2592000: #60*60*24*30
                current_1mon_sliding_data.append(row)

    last_recorded_timestamp = 0
    if len(current_1mon_sliding_data) > 0:
        last_recorded_timestamp = time.mktime(datetime.datetime.strptime(current_1mon_sliding_data[len(current_1mon_sliding_data)-1][0],
                                                           '%Y-%m-%d %H:%M:%S').timetuple())

    if int(time.time())-last_recorded_timestamp > 3600:
        current_24h_sliding_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, '24h_sliding.csv')
        price_high = 0.0
        price_low = 0.0
        price_sum = Decimal(DEC_PLACES)
        index = 0
        with open(current_24h_sliding_file_path, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            header_passed = False
            for row in csvreader:
                if not header_passed:
                    header_passed = True
                    continue
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
                price_avg = (price_sum / Decimal(index)).quantize(DEC_PLACES)
            except(ZeroDivisionError):
                price_avg = DEC_PLACES

        current_1mon_sliding_data.append([datetime.datetime.strftime(datetime.datetime.fromtimestamp(last_timestamp), '%Y-%m-%d %H:%M:%S'),
                                          price_high,
                                          price_low,
                                          price_avg,
                                          ])

        with open(current_1h_1mon_sliding_file_path, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',')
            csvwriter.writerow(['datetime','high','low','average'])
            for row in current_1mon_sliding_data:
                csvwriter.writerow(row)


def write_forever_csv(currency_code, total_sliding_volume, last_timestamp):
    current_forever_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, 'forever.csv')

    if not os.path.exists(os.path.join(current_forever_file_path)) or os.path.getsize(current_forever_file_path) == 0:
        with open(current_forever_file_path, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',')
            csvwriter.writerow(['datetime','high','low','average','volume'])

    last_recorded_timestamp = 0
    with open(current_forever_file_path, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        header_passed = False
        for row in csvreader:
            if not header_passed:
                header_passed = True
                continue
            last_recorded_timestamp = time.mktime(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').timetuple())

    if last_timestamp - last_recorded_timestamp > 86400: #60*60*24
        current_24h_sliding_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, '24h_sliding.csv')
        price_high = 0.0
        price_low = 0.0
        price_sum = Decimal(DEC_PLACES)
        index = 0
        with open(current_24h_sliding_file_path, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            header_passed = False
            for row in csvreader:
                if not header_passed:
                    header_passed = True
                    continue
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
                price_avg = (price_sum / Decimal(index)).quantize(DEC_PLACES)
            except(ZeroDivisionError):
                price_avg = DEC_PLACES


        with open(current_forever_file_path, 'ab') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',')
            csvwriter.writerow([datetime.datetime.strftime(datetime.datetime.fromtimestamp(last_timestamp), '%Y-%m-%d %H:%M:%S'),
                                price_high,
                                price_low,
                                price_avg,
                                total_sliding_volume,
                                ])


def write_volumes_csv(currency_code, currency_data, last_timestamp):
    current_volumes_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, 'volumes.csv')


