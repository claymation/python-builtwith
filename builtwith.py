import requests


ENDPOINTS_BY_API_VERSION = {1: 'http://api.builtwith.com/v1/api.json',
                            2: 'http://api.builtwith.com/v2/api.json'}


VERSION_EXCEPTION_TEMPLATE = "Version %s"


class UnsupportedApiVersion(NotImplementedError):
    pass


class BuiltWith(object):
    """
    BuiltWith API version client.

    V1:

    >>> from builtwith import BuiltWith
    >>> bw = BuiltWith(YOUR_API_KEY)
    >>> bw.lookup(URL)

    V2:

    >>> from builtwith import BuiltWith
    >>> bw = BuiltWith(YOUR_API_KEY, api_version=2)
    >>> bw.lookup(URL)
    """
    
    def __init__(self, key, api_version=1):
        if api_version not in ENDPOINTS_BY_API_VERSION.keys():
            raise UnsupportedApiVersion(VERSION_EXCEPTION_TEMPLATE % (api_version))

        self.key = key
        self.api_version = api_version

    def lookup(self, domain):
        """
        Lookup BuiltWith results for the given domain.
        """
        params = {
            'KEY': self.key,
            'LOOKUP': domain,
        }
        response = requests.get(ENDPOINTS_BY_API_VERSION[self.api_version],
                                params=params)
        return response.json()
