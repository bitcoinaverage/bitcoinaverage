#!/usr/bin/env python

import twitter
from bitcoinaverage.twitter_config import api
import time
import requests

# requires  http://code.google.com/p/python-twitter/
# https://github.com/bear/python-twitter.git

URL = "http://api.bitcoinaverage.com/ticker/USD"

while True:
    
    r = requests.get(URL).json()
    
    status = "Average USD Rates - Last: %s / Ask: %s / Bid: %s / 24h: %s" % (r['last'],r['ask'],r['bid'],r['24h_avg'])
    
    status = api.PostUpdate(status)
    print status.text
    
    time.sleep(60*60*4)