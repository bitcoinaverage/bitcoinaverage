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
        #-60 added because otherwise the timestamp will point to the the beginning of next period and not current
        current_24h_sliding_data.append([datetime.datetime.strftime(datetime.datetime.fromtimestamp(last_timestamp-60), '%Y-%m-%d %H:%M:%S'),
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
        #-3600 added because otherwise the timestamp will point to the the beginning of next period and not current
        current_1mon_sliding_data.append([datetime.datetime.strftime(datetime.datetime.fromtimestamp(last_timestamp-3600), '%Y-%m-%d %H:%M:%S'),
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
            #-86400 added because otherwise the timestamp will point to the the beginning of next period and not current
            csvwriter.writerow([datetime.datetime.strftime(datetime.datetime.fromtimestamp(last_timestamp-86400), '%Y-%m-%d %H:%M:%S'),
                                price_high,
                                price_low,
                                price_avg,
                                total_sliding_volume,
                                ])


def write_volumes_csv(currency_code, currency_data, last_timestamp):
    current_volumes_file_path = os.path.join(ba.server.HISTORY_DOCUMENT_ROOT, currency_code, 'volumes.csv')


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

    if last_timestamp - last_recorded_timestamp > 86400: #60*60*24
        for exchange in currency_data['exchanges']:
            if exchange not in exchanges_order:
                exchanges_order.append(exchange)
                headers.append('%s BTC' % exchange)
                headers.append('%s %%' % exchange)

        new_data_row = []
        new_data_row.append(datetime.datetime.strftime(datetime.datetime.fromtimestamp(last_timestamp-86400), '%Y-%m-%d %H:%M:%S'))
        new_data_row.append(currency_data[currency_code]['averages']['total_vol'])


        with open(current_volumes_file_path, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',')
            csvwriter.writerow([datetime.datetime.strftime(datetime.datetime.fromtimestamp(last_timestamp), '%Y-%m-%d %H:%M:%S'),
                                price_high,
                                price_low,
                                price_avg,
                                total_sliding_volume,
                                ])





"""
 "USD": {
    "averages": {
      "ask": "137.38",
      "bid": "136.75",
      "last": "137.25",
      "total_vol": "28708.04"
    },
    "exchanges": {
      "bitbox": {
        "rates": {
          "ask": "134.99",
          "bid": "131.29",
          "last": "134.99"
        },
        "source": "bitcoincharts",
        "volume_btc": "118.27",
        "volume_percent": "0.41"
      },
      "bitkonan": {
        "rates": {
          "ask": "144.00",
          "bid": "137.00",
          "last": "140.00"
        },
        "source": "bitcoincharts",
        "volume_btc": "8.50",
        "volume_percent": "0.03"
      },
      "bitstamp": {
        "rates": {
          "ask": "129.93",
          "bid": "129.91",
          "last": "129.93"
        },
        "source": "api",
        "volume_btc": "9640.58",
        "volume_percent": "33.58"
      },
      "btce": {
        "rates": {
          "ask": "123.60",
          "bid": "123.60",
          "last": "123.60"
        },
        "source": "api",
        "volume_btc": "2612.33",
        "volume_percent": "9.10"
      },
      "campbx": {
        "rates": {
          "ask": "127.79",
          "bid": "126.22",
          "last": "127.79"
        },
        "source": "bitcoincharts",
        "volume_btc": "617.10",
        "volume_percent": "2.15"
      },
      "cryptotrade": {
        "rates": {
          "ask": "123.80",
          "bid": "123.50",
          "last": "123.50"
        },
        "source": "api",
        "volume_btc": "8.58",
        "volume_percent": "0.03"
      },
      "fbtc": {
        "rates": {
          "ask": "135.00",
          "bid": "116.00",
          "last": "125.00"
        },
        "source": "bitcoincharts",
        "volume_btc": "22.00",
        "volume_percent": "0.08"
      },
      "icbit": {
        "rates": {
          "ask": "150.00",
          "bid": "85.00",
          "last": "140.00"
        },
        "source": "bitcoincharts",
        "volume_btc": "0.00",
        "volume_percent": "0.00"
      },
      "localbitcoins": {
        "rates": {
          "ask": "146.33",
          "bid": "None",
          "last": "146.33"
        },
        "source": "api",
        "volume_btc": "1285.30",
        "volume_percent": "4.48"
      },
      "mtgox": {
        "rates": {
          "ask": "144.50",
          "bid": "144.25",
          "last": "144.25"
        },
        "source": "api",
        "volume_btc": "14394.55",
        "volume_percent": "50.14"
      },
      "vircurex": {
        "rates": {
          "ask": "132.73",
          "bid": "132.00",
          "last": "132.73"
        },
        "source": "api",
        "volume_btc": "0.83",
        "volume_percent": "0.00"
      }
    }
  },

  """