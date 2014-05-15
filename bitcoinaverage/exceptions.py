class NoVolumeException(Exception):
    exchange_name = None
    strerror = u'volume data not available'

class NoApiException(Exception):
    exchange_name = None
    strerror = u'API not available'

class CallTimeoutException(Exception):
    exchange_name = None
    strerror = u'unreachable since %s UTC'

    def __str__(self):
        return "CallTimeoutException"

class CacheTimeoutException(Exception):
    exchange_name = None
    strerror = u'unreachable since %s UTC'
