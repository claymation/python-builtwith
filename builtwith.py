import requests

class BuiltWith(object):
    """
    BuiltWith API version 1 client.

    >>> from builtwith import BuiltWith
    >>> bw = BuiltWith(YOUR_API_KEY)
    >>> bw.lookup(URL)
    """

    ENDPOINT = 'http://api.builtwith.com/v1/api.json'

    def __init__(self, key):
        self.key = key

    def lookup(self, domain):
        """
        Lookup BuiltWith results for the given domain.
        """
        params = {
            'KEY': self.key,
            'LOOKUP': domain,
        }
        response = requests.get(self.ENDPOINT, params=params)
        return response.json()
