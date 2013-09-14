#!/usr/bin/env python

import twitter
from bitcoinaverage.twitter_config import api

# requires  http://code.google.com/p/python-twitter/
# https://github.com/bear/python-twitter.git

status = api.PostUpdate('test')
print status.text
