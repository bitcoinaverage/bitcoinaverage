#!/usr/bin/python2.7
import time
import logging

import redis
import simplejson as json

from bitcoinaverage import api_parsers
from bitcoinaverage.config import API_QUERY_FREQUENCY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s [%(levelname)s] :: %(message)s",
    handlers=[logging.StreamHandler()])
logger = logging.getLogger("parser_daemon")

logger.info("started API parser daemon")

red = redis.StrictRedis(host="localhost", port=6379, db=0)

while True:
    start_time = time.time()

    exchanges_rates, exchanges_ignored = api_parsers.callAll()
    red.delete("ba:exchanges", "ba:exchanges_ignored")
    for exchange_data in exchanges_rates:
        red.hset("ba:exchanges",
                 exchange_data['exchange_name'],
                 json.dumps(exchange_data, use_decimal=True))
    for exchange_name, exchange_ignore_reason in exchanges_ignored.iteritems():
        red.hset("ba:exchanges_ignored",
                 exchange_name,
                 exchange_ignore_reason)

    cycle_time = time.time() - start_time
    sleep_time = max(0, API_QUERY_FREQUENCY['_all'] - cycle_time)
    logger.info("spent {0}, sleeping {1}".format(cycle_time, sleep_time))
    time.sleep(sleep_time)
