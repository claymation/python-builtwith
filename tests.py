from httpretty import HTTPretty, httprettified

from builtwith import BuiltWith


@httprettified
def test_lookup():
    bw = BuiltWith('key')
    HTTPretty.register_uri(HTTPretty.GET, 'http://api.builtwith.com/v1/api.json', body='true')

    result = bw.lookup('example.com')

    qs = HTTPretty.last_request.querystring
    assert qs.get('KEY') == ['key']
    assert qs.get('LOOKUP') == ['example.com']
    assert result is True
