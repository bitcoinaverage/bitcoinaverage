import os
import time
import json
from email import utils

import bitcoinaverage as ba

def write_config():
    global ba

    js_config_template = """
var config = {'apiIndexUrl': $API_INDEX_URL,
              'apiIndexUrlNoGox': $API_INDEX_NOGOX_URL,
              'refreshRate': $refreshRate,
              'currencyOrder': $currencyOrder
                };
                    """
    config_string = js_config_template
    config_string = config_string.replace('$API_INDEX_URL', '"%s"' % ba.server.API_INDEX_URL)
    config_string = config_string.replace('$API_INDEX_NOGOX_URL', '"%s"' % ba.server.API_INDEX_URL_NOGOX)
    config_string = config_string.replace('$refreshRate', str(ba.config.FRONTEND_QUERY_FREQUENCY))
    config_string = config_string.replace('$currencyOrder', json.dumps(ba.config.CURRENCY_LIST))

    with open(os.path.join(ba.server.WWW_DOCUMENT_ROOT, 'config.js'), 'w') as config_file:
        config_file.write(config_string)


def write_log(log_string, message_type='ERROR'):
    timestamp = utils.formatdate(time.time())

    with open(ba.server.LOG_PATH, 'a') as log_file:
        log_string = '%s; %s: %s' % (timestamp, message_type, log_string)
        print log_string
        log_file.write(log_string+'\n')
