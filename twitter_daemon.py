#!/usr/bin/env python

import time
import logging

import twitter
import simplejson
import requests

from bitcoinaverage.twitter_config import api

logger = logging.getLogger("twitter_daemon")

URL = "https://api.bitcoinaverage.com/ticker/global/USD"

change = 0
oldprice = 0
perc = 0
direction = ""

while True:
    try:
        r = requests.get(URL).json()
    except(simplejson.decoder.JSONDecodeError, requests.exceptions.ConnectionError):
        time.sleep(2)
        continue

    newprice = r['last']
    
    if oldprice > newprice:
        b = oldprice - newprice
        change = round(b, 2)
        direction = "down"
        if oldprice != 0:
            a = (change / oldprice)*100
            perc = round(a, 2)
    elif oldprice < newprice:
        b = newprice - oldprice
        change = round(b, 2)
        direction = "up"
        if oldprice != 0:
            a = (change / oldprice)*100
            perc = round(a, 2)
            
    if perc != 0 and change != 0 and direction != "":
        status = "BitcoinAverage price index: ${0} ({1} ${2}) - https://BitcoinAverage.com".format(newprice,direction,change)
    else:
        status = "BitcoinAverage price index: ${0} - https://BitcoinAverage.com".format(newprice)

    try:
        result = api.PostUpdate(status)
    except twitter.TwitterError, err:
        logger.error("Twitter error: {0}".format(str(err)))
    else:
        oldprice = newprice

    time.sleep(3600)
