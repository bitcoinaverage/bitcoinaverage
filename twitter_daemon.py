#!/usr/bin/env python

import twitter
from bitcoinaverage.twitter_config import api
import time
import requests

# requires  http://code.google.com/p/python-twitter/
# https://github.com/bear/python-twitter.git

URL = "http://api.bitcoinaverage.com/ticker/USD"

change = 0
oldprice = 0
perc = 0

while True:
    
    r = requests.get(URL).json()
    newprice = r['last']
    
    if oldprice > newprice:
        change = oldprice - newprice
        direction = "down"
        print change
        print oldprice
        if oldprice != 0:
            perc = (change / oldprice)*100

    elif oldprice < newprice:
        change = newprice - oldprice
        direction = "up"
        print change
        print oldprice
        if oldprice != 0:
            perc = str((change / oldprice)*100)
            
    if perc != 0 and change != 0:
        print "Average USD Rate: $%s (%s $%s, %%s) - http://bitcoinaverage.com" % (newprice,direction,change,perc)
    else:
        print "Average USD Rate: $%s - http://bitcoinaverage.com" % (newprice)
        
    oldprice = newprice
    
    #status = "Average USD Rate: $%s (%s $%s, %%s) - http://bitcoinaverage.com" % (newprice,direction,change,perc)
    
    #status = api.PostUpdate(status)
    
    time.sleep(60)