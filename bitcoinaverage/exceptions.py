
class NoVolumeException(Exception):
    text = u'volume data not available'

class NoApiException(Exception):
    text = u'API not available'

class UnknownException(Exception):
    text = u'unknown error'
