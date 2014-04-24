import datetime
import unittest

from httpretty import HTTPretty, httprettified

from builtwith import (BuiltWithDomainInfo, BuiltWith, UnsupportedApiVersion,
                       ENDPOINTS_BY_API_VERSION, VERSION_EXCEPTION_TEMPLATE)


API_VERSION_ONE = 1
API_VERSION_TWO = 2
UNSUPPORTED_API_VERSION = 3

TEST_FULL_SCAN_DATE = datetime.date(2013, 5, 30)
TEST_DATETIME = datetime.datetime(2012, 9, 6, 23, 0)
TEST_DATETIME_STRING = u'/Date(1346972400000)/'

TEST_RESPONSE_JSON = {
  u'Paths': [{u'Url': u'',
              u'Domain': u'example.com',
              u'SubDomain': u'',
              u'Technologies': [{u'Name': u'HTML5 DocType',
                                 u'FirstDetected': TEST_DATETIME_STRING,
                                 u'Tag': u'docinfo',
                                 u'Link': u'http://dev.w3.org/html5/spec/syntax.html#the-doctype',
                                 u'LastDetected': TEST_DATETIME_STRING,
                                 u'Description': u'The DOCTYPE is a required preamble for HTML5 websites.'},
                                {u'Name': u'Javascript',
                                 u'FirstDetected': TEST_DATETIME_STRING,
                                 u'Tag': u'docinfo',
                                 u'Link': u'http://en.wikipedia.org/wiki/JavaScript',
                                 u'LastDetected': TEST_DATETIME_STRING,
                                 u'Description': u'JavaScript is a scripting language most often used for '
                                                 'client-side web development. Its proper name is ECMAScript, '
                                                 'though "JavaScript" is much more commonly used. The website '
                                                 'uses JavaScript.'}]},
             {u'Url': u'',
              u'Domain': u'example.com',
              u'SubDomain': u'test',
              u'Technologies': [{u'Name': u'HTML5 DocType',
                                 u'FirstDetected': TEST_DATETIME_STRING,
                                 u'Tag': u'docinfo',
                                 u'Link': u'http://dev.w3.org/html5/spec/syntax.html#the-doctype',
                                 u'LastDetected': TEST_DATETIME_STRING,
                                 u'Description': u'The DOCTYPE is a required preamble for HTML5 websites.'},
                                {u'Name': u'Javascript',
                                 u'FirstDetected': TEST_DATETIME_STRING,
                                 u'Tag': u'docinfo',
                                 u'Link': u'http://en.wikipedia.org/wiki/JavaScript',
                                 u'LastDetected': TEST_DATETIME_STRING,
                                 u'Description': u'JavaScript is a scripting language most often used for '
                                                 'client-side web development. Its proper name is ECMAScript, '
                                                 'though "JavaScript" is much more commonly used. The website '
                                                 'uses JavaScript.'}]}]}

class BuiltWithTests(unittest.TestCase):

    @httprettified
    def test_lookup(self):
        bw = BuiltWith('key')
        HTTPretty.register_uri(HTTPretty.GET, ENDPOINTS_BY_API_VERSION[API_VERSION_ONE], body='true')

        result = bw.lookup('example.com', last_full_query=True)

        qs = HTTPretty.last_request.querystring
        self.assertEqual(qs.get('KEY'), ['key'])
        self.assertEqual(qs.get('LOOKUP'), ['example.com'])
        self.assertTrue(result)


    @httprettified
    def test_lookup_alternate_version(self):
        bw = BuiltWith('key', api_version=API_VERSION_TWO)


        HTTPretty.register_uri(HTTPretty.GET, ENDPOINTS_BY_API_VERSION[API_VERSION_TWO],
                               body='{"Paths": []}')

        HTTPretty.register_uri(HTTPretty.GET, ENDPOINTS_BY_API_VERSION[API_VERSION_TWO],
                               body='{"TOPSITE": "2013-06-19", "FULL": "%s"}' % TEST_FULL_SCAN_DATE)

        result = bw.lookup('example.com', last_full_query=True)

        qs = HTTPretty.last_request.querystring
        self.assertEqual(qs.get('KEY'), ['key'])
        self.assertEqual(qs.get('LOOKUP'), ['example.com'])
        self.assertTrue(result)
        self.assertIsInstance(result, BuiltWithDomainInfo)
        self.assertDictEqual({'Paths': []}, result.api_response_json)


    @httprettified
    def test_unsupported_version(self):
        exception_raised = False

        try:
            BuiltWith('key', api_version=UNSUPPORTED_API_VERSION)
        except UnsupportedApiVersion as e:
            exception_raised = True
            self.assertEqual(VERSION_EXCEPTION_TEMPLATE % UNSUPPORTED_API_VERSION, str(e))

        self.assertTrue(exception_raised)


    @httprettified
    def test_domain_info_object(self):
        domain_info = BuiltWithDomainInfo(TEST_RESPONSE_JSON, last_full_builtwith_scan_date=TEST_FULL_SCAN_DATE)

        self.assertListEqual(sorted([(u'example.com', u'', u''), (u'example.com', u'test', u'')]),
                             sorted(domain_info.available_urls()))

        url_technologies = domain_info.get_technologies_by_url(domain='example.com', subdomain='', path='')

        self.assertListEqual(sorted(['HTML5 DocType', 'Javascript']), sorted(url_technologies.list_technologies()))

        js_info = url_technologies.get_technology_info('Javascript')

        self.assertEqual(js_info['Name'], 'Javascript')
        self.assertEqual(js_info['LastDetected'], TEST_DATETIME)
        self.assertFalse(js_info['CurrentlyLive'])

        html5_info = url_technologies.get_technology_info('HTML5 DocType')
        self.assertEqual(html5_info['Name'], 'HTML5 DocType')
        self.assertEqual(html5_info['LastDetected'], TEST_DATETIME)
        self.assertFalse(html5_info['CurrentlyLive'])
