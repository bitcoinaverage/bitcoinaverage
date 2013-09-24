#!/usr/bin/env python

import twitter
from bitcoinaverage.twitter_config import api
import time
import requests

# requires  http://code.google.com/p/python-twitter/
# https://github.com/bear/python-twitter.git

URL = "https://api.bitcoinaverage.com/ticker/USD"

change = 0
oldprice = 0
perc = 0
direction = ""

while True:
    
    r = requests.get(URL).json()
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
        status = "Average USD Rate: ${0} ({1} ${2}, %{3}) - https://BitcoinAverage.com".format(newprice,direction,change,perc)
        status = api.PostUpdate(status)
    else:
        status = "Average USD Rate: ${0} - https://BitcoinAverage.com".format(newprice)
        status = api.PostUpdate(status)
        
    oldprice = newprice

    time.sleep(60*60*4)