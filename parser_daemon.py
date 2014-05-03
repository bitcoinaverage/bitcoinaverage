#!/usr/bin/python2.7
import time
import logging

import redis
import simplejson as json
import eventlet

from bitcoinaverage import api_parsers
from bitcoinaverage.config import API_QUERY_FREQUENCY, EXCHANGE_LIST

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s [%(levelname)s] :: %(message)s",
    handlers=[logging.StreamHandler()])
logger = logging.getLogger("parser_daemon")

logger.info("started API parser daemon")

red = redis.StrictRedis(host="localhost", port=6379, db=0)
red.delete("ba:exchanges", "ba:exchanges_ignored")  # Reset

pool = eventlet.GreenPool()
queue = eventlet.Queue()

def worker(exchange_name, q):
    result = api_parsers.callAPI(exchange_name)
    q.put(result)

for exchange_name in EXCHANGE_LIST:
    pool.spawn_n(worker, exchange_name, queue)

while True:
    start_time = time.time()

    results = []
    while not queue.empty():
        results.append(queue.get())

    for exchange_name, exchange_data, exchange_ignore_reason in results:
        if exchange_ignore_reason is None:
            red.hset("ba:exchanges",
                     exchange_name,
                     json.dumps(exchange_data, use_decimal=True))
            red.hdel("ba:exchanges_ignored", exchange_name)
        else:
            red.hset("ba:exchanges_ignored",
                     exchange_name,
                     exchange_ignore_reason)
            red.hdel("ba:exchanges", exchange_name)
        pool.spawn_n(worker, exchange_name, queue)
    logger.info("saved {0} results".format(len(results)))

    cycle_time = time.time() - start_time
    sleep_time = max(0, API_QUERY_FREQUENCY['_all'] - cycle_time)
    logger.info("spent {0}, sleeping {1}".format(cycle_time, sleep_time))
    eventlet.sleep(sleep_time)
