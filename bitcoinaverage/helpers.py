import os
import time
import json
from email import utils

from bitcoinaverage.config import FRONTEND_QUERY_FREQUENCY, CURRENCY_LIST
from bitcoinaverage.server import WWW_DOCUMENT_ROOT, API_INDEX_URL, LOG_PATH

def write_config(project_abs_path):
    global WWW_DOCUMENT_ROOT, CURRENCY_LIST

    config_template = """
var config = {'apiIndexUrl': $API_INDEX_URL,
              'refreshRate': $refreshRate,
              'currencyOrder': $currencyOrder
                };
                    """

    if WWW_DOCUMENT_ROOT == '':
        WWW_DOCUMENT_ROOT = os.path.join(project_abs_path, 'www')

    config_string = config_template.replace('$API_INDEX_URL', '"'+API_INDEX_URL+'"')
    config_string = config_string.replace('$refreshRate', str(FRONTEND_QUERY_FREQUENCY))
    config_string = config_string.replace('$currencyOrder', json.dumps(CURRENCY_LIST))

    with open(os.path.join(WWW_DOCUMENT_ROOT, 'config.js'), "w") as config_file:
        config_file.write(config_string)


def write_log(log_path, log_string, message_type='ERROR'):
    timestamp = utils.formatdate(time.time())

    with open(log_path, 'a') as log_file:
        log_string = '%s; %s: %s \n' % (timestamp, message_type, log_string)
        print log_string
        log_file.write(log_string)
