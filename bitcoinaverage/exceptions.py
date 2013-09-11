class NoVolumeException(Exception):
    exchange_name = None
    text = u'volume data not available'

class NoApiException(Exception):
    exchange_name = None
    text = u'API not available'

class CallTimeoutException(Exception):
    exchange_name = None
    text = u'API call failed'

class CacheTimeoutException(Exception):
    exchange_name = None
    text = u'unreachable since %s UTC'
