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
    for exchange in exchanges_rates:
        red.hset("ba:exchanges",
                 exchange['exchange_name'],
                 json.dumps(exchange, use_decimal=True))
    red.set("ba:ignored", json.dumps(exchanges_ignored))

    cycle_time = time.time() - start_time
    sleep_time = max(0, API_QUERY_FREQUENCY['default'] - cycle_time)
    logger.info("spent {0}, sleeping {1}".format(cycle_time, sleep_time))
    time.sleep(sleep_time)
