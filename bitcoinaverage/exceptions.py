
class NoVolumeException(Exception):
    exchange_name = None
    text = u'volume data not available'

class NoApiException(Exception):
    exchange_name = None
    text = u'API not available'

class UnknownException(Exception):
    exchange_name = None
    text = u'unknown error'

class CallFailedException(Exception):
    exchange_name = None
    text = u'unreachable since %s UTC'
