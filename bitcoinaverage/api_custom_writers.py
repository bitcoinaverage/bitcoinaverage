import os
import subprocess
import sys
import csv
from copy import deepcopy
import StringIO
from decimal import Decimal, InvalidOperation
import simplejson
from eventlet.green import urllib2
from eventlet.green import httplib
from eventlet.timeout import Timeout
import socket
import json

import bitcoinaverage as ba
import bitcoinaverage.server as server
from bitcoinaverage.config import DEC_PLACES, FRONTEND_MAJOR_CURRENCIES, CURRENCY_LIST, API_FILES, CUSTOM_API_FILES
from bitcoinaverage.exceptions import CallTimeoutException
import bitcoinaverage.helpers as helpers


def createCustomAPIs(api_document_root,
                     human_timestamp,
                     calculated_average_rates_formatted,
                     calculated_volumes_formatted,
                     calculated_global_average_rates_formatted,
                     exchanges_ignored):

    if not os.path.exists(os.path.join(api_document_root, API_FILES['CUSTOM_API'])):
        os.makedirs(os.path.join(api_document_root, API_FILES['CUSTOM_API']))

    globals_list = globals()
    for globals_item in globals_list:
        if globals_item.startswith('_writeCustomAPI_'):
            globals()[globals_item](api_document_root,
                                     human_timestamp,
                                     calculated_average_rates_formatted,
                                     calculated_volumes_formatted,
                                     calculated_global_average_rates_formatted,
                                     exchanges_ignored)

def _writeCustomAPI_AndroidBitcoinWallet(api_path,
                                         human_timestamp,
                                         calculated_average_rates_formatted,
                                         calculated_volumes_formatted,
                                         calculated_global_average_rates_formatted,
                                         exchanges_ignored):

    result = {}
    major_currencies = []
    index = 0
    for currency_code in CURRENCY_LIST:
        major_currencies.append(currency_code)
        index = index + 1
        if index == FRONTEND_MAJOR_CURRENCIES:
            break

    for currency_code in calculated_global_average_rates_formatted:
        if "24h_avg" in calculated_global_average_rates_formatted[currency_code]:
            result[currency_code] = {'24h_avg': calculated_global_average_rates_formatted[currency_code]['24h_avg']}
        elif "last" in calculated_global_average_rates_formatted[currency_code]:
            result[currency_code] = {'last': calculated_global_average_rates_formatted[currency_code]['last']}

    helpers.write_api_file(
        os.path.join(api_path, API_FILES['CUSTOM_API'], CUSTOM_API_FILES['AndroidBitcoinWallet']),
        json.dumps(result))

def _writeCustomAPI_HiveMacDesktopWallet(api_path,
                                         human_timestamp,
                                         calculated_average_rates_formatted,
                                         calculated_volumes_formatted,
                                         calculated_global_average_rates_formatted,
                                         exchanges_ignored):

    result = {}
    major_currencies = []
    index = 0
    for currency_code in CURRENCY_LIST:
        major_currencies.append(currency_code)
        index = index + 1
        if index == FRONTEND_MAJOR_CURRENCIES:
            break

    for currency_code in calculated_global_average_rates_formatted:
        if "24h_avg" in calculated_global_average_rates_formatted[currency_code]:
            result[currency_code] = {'24h_avg': calculated_global_average_rates_formatted[currency_code]['24h_avg']}
        elif "last" in calculated_global_average_rates_formatted[currency_code]:
            result[currency_code] = {'last': calculated_global_average_rates_formatted[currency_code]['last']}

    helpers.write_api_file(
        os.path.join(api_path, API_FILES['CUSTOM_API'], CUSTOM_API_FILES['AndroidBitcoinWallet']),
        json.dumps(result))

def _writeCustomAPI_HiveAndroidWallet(api_path,
                                         human_timestamp,
                                         calculated_average_rates_formatted,
                                         calculated_volumes_formatted,
                                         calculated_global_average_rates_formatted,
                                         exchanges_ignored):

    result = {}
    major_currencies = []
    index = 0
    for currency_code in CURRENCY_LIST:
        major_currencies.append(currency_code)
        index = index + 1
        if index == FRONTEND_MAJOR_CURRENCIES:
            break

    for currency_code in calculated_global_average_rates_formatted:
        if "24h_avg" in calculated_global_average_rates_formatted[currency_code]:
            result[currency_code] = {'24h_avg': calculated_global_average_rates_formatted[currency_code]['24h_avg']}
        elif "last" in calculated_global_average_rates_formatted[currency_code]:
            result[currency_code] = {'last': calculated_global_average_rates_formatted[currency_code]['last']}

    helpers.write_api_file(
        os.path.join(api_path, API_FILES['CUSTOM_API'], CUSTOM_API_FILES['AndroidBitcoinWallet']),
        json.dumps(result))
