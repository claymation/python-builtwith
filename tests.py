from httpretty import HTTPretty, httprettified

from builtwith import BuiltWith, UnsupportedApiVersion, ENDPOINTS_BY_API_VERSION, VERSION_EXCEPTION_TEMPLATE


@httprettified
def test_lookup():
    API_VERSION_TESTED = 1

    bw = BuiltWith('key')
    HTTPretty.register_uri(HTTPretty.GET, ENDPOINTS_BY_API_VERSION[API_VERSION_TESTED], body='true')

    result = bw.lookup('example.com')

    qs = HTTPretty.last_request.querystring
    assert qs.get('KEY') == ['key']
    assert qs.get('LOOKUP') == ['example.com']
    assert result is True


@httprettified
def test_lookup_alternate_version():
    API_VERSION_TESTED = 2

    bw = BuiltWith('key', api_version=API_VERSION_TESTED)
    HTTPretty.register_uri(HTTPretty.GET, ENDPOINTS_BY_API_VERSION[API_VERSION_TESTED], body='true')

    result = bw.lookup('example.com')

    qs = HTTPretty.last_request.querystring
    assert qs.get('KEY') == ['key']
    assert qs.get('LOOKUP') == ['example.com']
    assert result is True

@httprettified
def test_unsupported_version():
    UNSUPPORTED_API_VERSION = 3

    try:
        bw = BuiltWith('key', api_version=UNSUPPORTED_API_VERSION)
    except UnsupportedApiVersion as e:
        assert VERSION_EXCEPTION_TEMPLATE % (UNSUPPORTED_API_VERSION) == str(e)
        return

    raise RuntimeError("UnsupportedApiVersion exception not raised when it should have been.")
