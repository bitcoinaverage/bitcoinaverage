import os
import time
import datetime
from decimal import Decimal
import csv
import json
import logging

import bitcoinaverage as ba
import bitcoinaverage.server
from bitcoinaverage import helpers
from bitcoinaverage.config import DEC_PLACES, CURRENCY_LIST

logger = logging.getLogger(__name__)


def write_24h_csv(currency_code, current_data, current_timestamp):
    current_24h_sliding_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, 'per_minute_24h_sliding_window.csv')

    current_24h_sliding_data = []

    #to create file if not exists
    with open(current_24h_sliding_file_path, 'a') as csvfile:
        pass

    #read file
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
    else:
        logger.warning("{0} is empty".format(current_24h_sliding_file_path))

    if current_timestamp - last_recorded_timestamp > 60*2:
        #-60 added because otherwise the timestamp will point to the the beginning of next period and not current
        current_24h_sliding_data.append([datetime.datetime.strftime(datetime.datetime.fromtimestamp(current_timestamp-60), '%Y-%m-%d %H:%M:%S'),
                                         current_data['last']])

    with open(current_24h_sliding_file_path, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(['datetime','average'])
        for row in current_24h_sliding_data:
            csvwriter.writerow(row)


def write_24h_global_average_csv(fiat_data_all , currency_data_all, currency_code,  current_timestamp):
    current_24h_sliding_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, 'per_minute_24h_global_average_sliding_window.csv')
    current_24h_sliding_data = []

    #to create file if not exists
    with open(current_24h_sliding_file_path, 'a') as csvfile:
        pass

    with open(current_24h_sliding_file_path, 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=',')
        for row in csvreader:
            last_recorded_timestamp = time.mktime(datetime.datetime.strptime(row['datetime'], '%Y-%m-%d %H:%M:%S').timetuple())
            if current_timestamp - last_recorded_timestamp < 86400: #60*60*24
                current_24h_sliding_data.append(row)

    last_recorded_timestamp = 0
    if len(current_24h_sliding_data) > 0:
        last_recorded_timestamp = time.mktime(datetime.datetime.strptime(current_24h_sliding_data[len(current_24h_sliding_data)-1]['datetime'],
                                                          '%Y-%m-%d %H:%M:%S').timetuple())
    else:
        logger.warning("{0} is empty".format(current_24h_sliding_file_path))

    if current_timestamp - last_recorded_timestamp > 60*2:
        new_row = {}
        #-60 added because otherwise the timestamp will point to the the beginning of next period and not current
        timestamp = datetime.datetime.strftime(datetime.datetime.fromtimestamp(current_timestamp-60), '%Y-%m-%d %H:%M:%S')
        new_row['datetime'] = timestamp

        cross_rate_divisor = float(fiat_data_all[currency_code]['rate'])

        for currency in CURRENCY_LIST:
            cross_rate_dividend = float(fiat_data_all[currency]['rate'])
            currency_volume = currency_data_all[currency]['averages']['total_vol']
            currency_average = currency_data_all[currency]['averages']['last']
            currency_rate = cross_rate_dividend / cross_rate_divisor #this is cross rate in USD
            new_row[currency + ' volume'] = currency_volume
            new_row[currency + ' average'] = currency_average
            new_row[currency + ' rate'] = currency_rate

        currency_global_average = currency_data_all[currency_code]['global_averages']['last']
        new_row[currency_code + ' global average'] = currency_global_average
        current_24h_sliding_data.append(new_row)

    csv_currency_titles = []

    csv_currency_titles.append('datetime')

    for currency in CURRENCY_LIST:
        csv_currency_titles.append(currency + ' ' + 'volume')
        csv_currency_titles.append(currency + ' ' + 'average')
        csv_currency_titles.append(currency + ' ' + 'rate')

    csv_currency_titles.append(currency_code + ' ' + 'global average')

    with open(current_24h_sliding_file_path, 'wb') as csvfile:
        csvwriter = csv.DictWriter(csvfile, csv_currency_titles, restval=0, extrasaction='ignore', delimiter=',')
        csvwriter.writeheader()
        for row in current_24h_sliding_data:
            csvwriter.writerow(row)


def write_24h_global_average_short_csv(currency_data_all, currency_code,  current_timestamp):
    current_24h_sliding_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, 'per_minute_24h_global_average_sliding_window_short.csv')
    current_24h_sliding_data = []

    #to create file if not exists
    with open(current_24h_sliding_file_path, 'a') as csvfile:
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
    else:
        logger.warning("{0} is empty".format(current_24h_sliding_file_path))

    if current_timestamp - last_recorded_timestamp > 60*2:
        row = []
        #-60 added because otherwise the timestamp will point to the the beginning of next period and not current
        timestamp = datetime.datetime.strftime(datetime.datetime.fromtimestamp(current_timestamp-60), '%Y-%m-%d %H:%M:%S')
        currency_global_average = currency_data_all[currency_code]['global_averages']['last']
        row.append(timestamp)
        row.append(currency_global_average)
        current_24h_sliding_data.append(row)

    csv_currency_titles = []

    csv_currency_titles.append('datetime')
    csv_currency_titles.append(currency_code + ' ' + 'global average')

    with open(current_24h_sliding_file_path, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow( csv_currency_titles )
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
    else:
        logger.warning("{0} is empty".format(current_1h_1mon_sliding_file_path))

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
                if current_timestamp - timestamp < 3600: #60*60
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
            # Last timestamp from the file points to the beginning of previous period
            last_recorded_timestamp = time.mktime(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').timetuple())

    timestamp_delta = datetime.timedelta(seconds=(current_timestamp - last_recorded_timestamp))
    if timestamp_delta >= datetime.timedelta(days=2):
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
                if current_timestamp - timestamp < 86400:  # 1 day
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
            new_data_row = [datetime.datetime.strftime(
                                datetime.datetime.fromtimestamp(current_timestamp - 86400),
                                '%Y-%m-%d 00:00:00'),
                            price_high,
                            price_low,
                            price_avg,
                            total_sliding_volume,
                            ]
            csvwriter.writerow(new_data_row)


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
        # Last timestamp from the file points to the beginning of previous period
        try:
            last_recorded_timestamp = time.mktime(datetime.datetime.strptime(current_volumes_data[len(current_volumes_data)-1][0],
                                                               '%Y-%m-%d %H:%M:%S').timetuple())
        except ValueError:
            last_recorded_timestamp = time.mktime(datetime.datetime.strptime(current_volumes_data[len(current_volumes_data)-1][0],
                                                               '%Y-%m-%d').timetuple())
    else:
        logger.warning("{0} is empty".format(current_volumes_file_path))

    timestamp_delta = datetime.timedelta(seconds=(current_timestamp - last_recorded_timestamp))
    if timestamp_delta >= datetime.timedelta(days=2):
        for exchange in currency_data['exchanges']:
            if exchange not in exchanges_order:
                exchanges_order.append(exchange)
                headers.append('%s BTC' % exchange)
                headers.append('%s %%' % exchange)

        new_data_row = []
        new_data_row.append(datetime.datetime.strftime(
            datetime.datetime.fromtimestamp(current_timestamp - 86400),
            '%Y-%m-%d 00:00:00'))
        new_data_row.append(currency_data['averages']['total_vol'])

        for exchange in exchanges_order:
            if exchange in currency_data['exchanges']:
                new_data_row.append(currency_data['exchanges'][exchange]['volume_btc'])
                new_data_row.append(currency_data['exchanges'][exchange]['volume_percent'])
            else:
                new_data_row.append(0)
                new_data_row.append(0)

        with open(current_volumes_file_path, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',')
            csvwriter.writerow(headers)
            for row in current_volumes_data:
                csvwriter.writerow(row)

            csvwriter.writerow(new_data_row)
