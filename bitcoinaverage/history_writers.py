import os
import time
import datetime
from decimal import Decimal
import csv
import json

import bitcoinaverage as ba
from bitcoinaverage.config import DEC_PLACES


def write_24h_csv(currency_code, current_data, current_timestamp):
    current_24h_sliding_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, 'per_minute_24h_sliding_window.csv')

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
            last_recorded_timestamp = time.mktime(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').timetuple())
            if current_timestamp - last_recorded_timestamp < 86400: #60*60*24
                current_24h_sliding_data.append(row)

    last_recorded_timestamp = 0
    if len(current_24h_sliding_data) > 0:
        last_recorded_timestamp = time.mktime(datetime.datetime.strptime(current_24h_sliding_data[len(current_24h_sliding_data)-1][0],
                                                           '%Y-%m-%d %H:%M:%S').timetuple())

    if current_timestamp - last_recorded_timestamp > 60*2:
        #-60 added because otherwise the timestamp will point to the the beginning of next period and not current
        current_24h_sliding_data.append([datetime.datetime.strftime(datetime.datetime.fromtimestamp(current_timestamp-60), '%Y-%m-%d %H:%M:%S'),
                                         current_data['last']])

    with open(current_24h_sliding_file_path, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(['datetime','average'])
        for row in current_24h_sliding_data:
            csvwriter.writerow(row)


def write_1mon_csv(currency_code, current_timestamp):
    current_1h_1mon_sliding_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, 'per_hour_monthly_sliding_window.csv')

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
            if current_timestamp - timestamp < 2592000: #60*60*24*30
                current_1mon_sliding_data.append(row)

    last_recorded_timestamp = 0
    if len(current_1mon_sliding_data) > 0:
        last_recorded_timestamp = time.mktime(datetime.datetime.strptime(current_1mon_sliding_data[len(current_1mon_sliding_data)-1][0],
                                                           '%Y-%m-%d %H:%M:%S').timetuple())

    if int(time.time())-last_recorded_timestamp > 3600*2:
        current_24h_sliding_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, 'per_minute_24h_sliding_window.csv')
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
                if current_timestamp - timestamp < 3600: #60*60*24
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
        #-3600 added because otherwise the timestamp will point to the the beginning of next period and not current
        current_1mon_sliding_data.append([datetime.datetime.strftime(datetime.datetime.fromtimestamp(current_timestamp-3600), '%Y-%m-%d %H:%M:%S'),
                                          price_high,
                                          price_low,
                                          price_avg,
                                          ])

        with open(current_1h_1mon_sliding_file_path, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',')
            csvwriter.writerow(['datetime','high','low','average'])
            for row in current_1mon_sliding_data:
                csvwriter.writerow(row)


def write_forever_csv(currency_code, total_sliding_volume, current_timestamp):
    current_forever_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, 'per_day_all_time_history.csv')

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

    if current_timestamp - last_recorded_timestamp > 86400*2: #60*60*24
        current_24h_sliding_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, 'per_minute_24h_sliding_window.csv')
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
                if current_timestamp - timestamp < 3600: #60*60*24
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
            #-86400 added because otherwise the timestamp will point to the the beginning of next period and not current
            csvwriter.writerow([datetime.datetime.strftime(datetime.datetime.fromtimestamp(current_timestamp-86400), '%Y-%m-%d %H:%M:%S'),
                                price_high,
                                price_low,
                                price_avg,
                                total_sliding_volume,
                                ])


def write_volumes_csv(currency_code, currency_data, current_timestamp):
    current_volumes_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, 'volumes.csv')

    with open(current_volumes_file_path, 'a') as csvfile: #to create file if not exists
        pass

    current_volumes_data = []
    exchanges_order = []
    headers = ['datetime', 'total_vol']
    with open(current_volumes_file_path, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        header_passed = False
        for row in csvreader:
            if not header_passed:
                for header in row:
                    if header == 'datetime' or header == 'total_vol':
                        continue
                    headers.append(header)
                    header = header.replace(' BTC', '')
                    header = header.replace(' %', '')
                    if header not in exchanges_order:
                        exchanges_order.append(header)


                header_passed = True
                continue
            current_volumes_data.append(row)

    last_recorded_timestamp = 0
    if len(current_volumes_data) > 0:
        last_recorded_timestamp = time.mktime(datetime.datetime.strptime(current_volumes_data[len(current_volumes_data)-1][0],
                                                           '%Y-%m-%d %H:%M:%S').timetuple())
    if current_timestamp - last_recorded_timestamp > 86400*2: #60*60*24; *2 because we check since start of yesterday till end of today
        for exchange in currency_data['exchanges']:
            if exchange not in exchanges_order:
                exchanges_order.append(exchange)
                headers.append('%s BTC' % exchange)
                headers.append('%s %%' % exchange)

        new_data_row = []
        new_data_row.append(datetime.datetime.strftime(datetime.datetime.fromtimestamp(current_timestamp-86400), '%Y-%m-%d %H:%M:%S'))
        new_data_row.append(currency_data['averages']['total_vol'])

        for exchange in exchanges_order:
            if exchange in currency_data['exchanges']:
                new_data_row.append(currency_data['exchanges'][exchange]['volume_btc'])
                new_data_row.append(currency_data['exchanges'][exchange]['volume_percent'])
            else:
                new_data_row.append(0)
                new_data_row.append(0)

        new_data_row.append(currency_data['averages']['total_vol'])

        with open(current_volumes_file_path, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',')
            csvwriter.writerow(headers)
            for row in current_volumes_data:
                csvwriter.writerow(row)

            csvwriter.writerow(new_data_row)


