import datetime
import unittest

from httpretty import HTTPretty, httprettified

import builtwith


API_VERSION_ONE = 1
API_VERSION_TWO = 2
UNSUPPORTED_API_VERSION = 3

TEST_EPOCH_TIME = 1346972400
TEST_DATETIME = datetime.datetime.utcfromtimestamp(TEST_EPOCH_TIME) # 2012-9-6
TEST_DATETIME_STRING = u'/Date(%s)/' % (TEST_EPOCH_TIME * 1000)

# Dates are named relative to the TEST_EPOCH_TIME
TEST_FULL_SCAN_DATE_BEFORE = datetime.date(2012, 5, 30)
TEST_FULL_SCAN_DATE_AFTER = datetime.date(2012, 10, 6)
TEST_TOPSITE_DATE = datetime.date(2012, 6, 19)

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
    def test_lookup_version_one(self):
        bw = builtwith.BuiltWith('key')
        HTTPretty.register_uri(HTTPretty.GET, builtwith.ENDPOINTS_BY_API_VERSION[API_VERSION_ONE], body='true')

        result = bw.lookup('example.com')

        qs = HTTPretty.last_request.querystring
        self.assertEqual(qs.get('KEY'), ['key'])
        self.assertEqual(qs.get('LOOKUP'), ['example.com'])
        self.assertTrue(result)


    @httprettified
    def test_lookup_version_two(self):
        bw = builtwith.BuiltWith('key', api_version=API_VERSION_TWO)


        HTTPretty.register_uri(HTTPretty.GET, builtwith.ENDPOINTS_BY_API_VERSION[API_VERSION_TWO],
                               body='{"Paths": []}')

        HTTPretty.register_uri(HTTPretty.GET, builtwith.ENDPOINTS_BY_API_VERSION[API_VERSION_TWO],
                               body='{"TOPSITE": "%s", "FULL": "%s"}' % (TEST_TOPSITE_DATE,
                                                                         TEST_FULL_SCAN_DATE_BEFORE))

        result = bw.lookup('example.com')

        qs = HTTPretty.last_request.querystring
        self.assertEqual(qs.get('KEY'), ['key'])
        self.assertEqual(qs.get('LOOKUP'), ['example.com'])
        self.assertTrue(result)
        self.assertIsInstance(result, builtwith.BuiltWithDomainInfo)
        self.assertDictEqual({'Paths': []}, result.api_response_json)


    @httprettified
    def test_unsupported_version(self):
        exception_raised = False

        try:
          builtwith.BuiltWith('key', api_version=UNSUPPORTED_API_VERSION)
        except builtwith.UnsupportedApiVersion as e:
            exception_raised = True
            self.assertEqual(builtwith.VERSION_EXCEPTION_TEMPLATE % UNSUPPORTED_API_VERSION, str(e))

        self.assertTrue(exception_raised)


    def test_domain_info_object(self):
        domain_info = builtwith.BuiltWithDomainInfo(TEST_RESPONSE_JSON)

        self.assertListEqual(sorted([(u'example.com', u'', u''), (u'example.com', u'test', u'')]),
                             sorted(domain_info.available_urls()))

        url_technologies = domain_info.get_technologies_by_url(domain='example.com', subdomain='', path='')

        self.assertListEqual(sorted(['HTML5 DocType', 'Javascript']), sorted(url_technologies.list_technologies()))

        js_info = url_technologies.get_technology_info('Javascript')

        self.assertEqual(js_info['Name'], 'Javascript')
        self.assertEqual(js_info['LastDetected'], TEST_DATETIME)
        self.assertEqual(None, js_info.get('CurrentlyLive'))

        html5_info = url_technologies.get_technology_info('HTML5 DocType')
        self.assertEqual(html5_info['Name'], 'HTML5 DocType')
        self.assertEqual(html5_info['LastDetected'], TEST_DATETIME)
        self.assertEqual(None, html5_info.get('CurrentlyLive'))


    def test_currently_live_fetching_with_scan_before(self):
        domain_info = builtwith.BuiltWithDomainInfo(TEST_RESPONSE_JSON,
                                                    last_full_builtwith_scan_date=TEST_FULL_SCAN_DATE_BEFORE)

        url_technologies = domain_info.get_technologies_by_url(domain='example.com', subdomain='', path='')

        js_info = url_technologies.get_technology_info('Javascript')

        self.assertEqual(js_info['Name'], 'Javascript')
        self.assertEqual(js_info['LastDetected'], TEST_DATETIME)
        self.assertTrue(js_info['CurrentlyLive'])

        html5_info = url_technologies.get_technology_info('HTML5 DocType')
        self.assertEqual(html5_info['Name'], 'HTML5 DocType')
        self.assertEqual(html5_info['LastDetected'], TEST_DATETIME)
        self.assertTrue(html5_info['CurrentlyLive'])


    def test_currently_live_fetching_with_scan_after(self):
      domain_info = builtwith.BuiltWithDomainInfo(TEST_RESPONSE_JSON,
                                                  last_full_builtwith_scan_date=TEST_FULL_SCAN_DATE_AFTER)

      url_technologies = domain_info.get_technologies_by_url(domain='example.com', subdomain='', path='')

      js_info = url_technologies.get_technology_info('Javascript')

      self.assertEqual(js_info['Name'], 'Javascript')
      self.assertEqual(js_info['LastDetected'], TEST_DATETIME)
      self.assertFalse(js_info['CurrentlyLive'])

      html5_info = url_technologies.get_technology_info('HTML5 DocType')
      self.assertEqual(html5_info['Name'], 'HTML5 DocType')
      self.assertEqual(html5_info['LastDetected'], TEST_DATETIME)
      self.assertFalse(html5_info['CurrentlyLive'])


    def test__convert_string_to_utc_datetime(self):
        converted_utc_datetime = builtwith._convert_string_to_utc_datetime(TEST_DATETIME_STRING)

        self.assertEqual(converted_utc_datetime, TEST_DATETIME)
