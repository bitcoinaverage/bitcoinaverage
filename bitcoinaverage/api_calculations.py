import csv
import StringIO
from decimal import Decimal, InvalidOperation
import decimal
import simplejson
from eventlet.green import urllib2
from eventlet.green import httplib
from eventlet.timeout import Timeout
import socket

import bitcoinaverage as ba
from bitcoinaverage.config import DEC_PLACES, API_CALL_TIMEOUT_THRESHOLD, API_REQUEST_HEADERS
from bitcoinaverage.exceptions import CallTimeoutException


def get24hAverage(currency_code):
    average_price = DEC_PLACES
    history_currency_API_24h_path = '%s%s/per_minute_24h_sliding_window.csv' % (ba.server.API_INDEX_URL_HISTORY, currency_code)

    try:
        with Timeout(API_CALL_TIMEOUT_THRESHOLD, CallTimeoutException):
            csv_result = urllib2.urlopen(urllib2.Request(url=history_currency_API_24h_path, headers=API_REQUEST_HEADERS)).read()
    except (
            KeyError,
            ValueError,
            socket.error,
            simplejson.decoder.JSONDecodeError,
            urllib2.URLError,
            httplib.BadStatusLine,
            CallTimeoutException):
        return 0

    csvfile = StringIO.StringIO(csv_result)
    csvreader = csv.reader(csvfile, delimiter=',')
    price_sum = DEC_PLACES
    index = 0
    header_passed = False
    for row in csvreader:
        if not header_passed:
            header_passed = True
            continue
        try:
            price_sum = price_sum + Decimal(row[1])
            index = index + 1
        except (IndexError, InvalidOperation):
            continue
    try:
        average_price = (price_sum / Decimal(index)).quantize(DEC_PLACES)
    except InvalidOperation:
        average_price = DEC_PLACES

    return average_price
