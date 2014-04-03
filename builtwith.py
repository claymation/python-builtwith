import datetime
import re
import requests


ENDPOINTS_BY_API_VERSION = {1: 'http://api.builtwith.com/v1/api.json',
                            2: 'http://api.builtwith.com/v2/api.json'}

VERSION_EXCEPTION_TEMPLATE = 'Version %s'

DATETIME_INFORMATION_NAMES = ['FirstDetected', 'LastDetected']


class UnsupportedApiVersion(NotImplementedError):
    pass


def _convert_string_to_utc_datetime(datetime_string):
    return datetime.datetime.utcfromtimestamp(
        int(re.search("\d+", datetime_string).group(0)) / 1000)


class UrlTechnologiesSet(object):

    def __init__(self, technologies_list, last_full_builtwith_scan=None):
        """
        Initializes the object using the list of technology dictionaries. Takes an optional parameter for the
        datetime.date object of the last full BuiltWith scan.
        """

        self._technologies_by_name = {}
        for technologies_dict in technologies_list:
            for name in DATETIME_INFORMATION_NAMES:
                technologies_dict[name] = _convert_string_to_utc_datetime(technologies_dict[name])

            # According to the team at BuiltWith, it's best to just use the last "FULL" scan
            # time in the CurrentlyLive determination since BuiltWith doesn't publish their
            # smaller "TOPSITE" list. Downside is that this client will say some technologies were
            # successfully detected on "TOPSITE" sites on the the last BuiltWith scan when that's
            # not in fact accurate.
            if last_full_builtwith_scan:
                technologies_dict['CurrentlyLive'] = (
                    last_full_builtwith_scan <= technologies_dict['LastDetected'].date())

            self._technologies_by_name[technologies_dict['Name']] = technologies_dict

    def __iter__(self):
        return iter(self._technologies_by_name.values())

    def get_technology_info(self, technology_name):
        return self._technologies_by_name.get(technology_name, None)

    def list_technologies(self):
        return self._technologies_by_name.keys()


class BuiltWithDomainInfo(object):

    def __init__(self, api_response_json, last_full_builtwith_scan=None):
        self.api_response_json = api_response_json
        self._technologies_by_url = {}
        for path_entry in api_response_json['Paths']:
            url_key = self.__get_url_key(
                path_entry['Domain'], path_entry.get('SubDomain', None), path_entry['Url'])
            self._technologies_by_url[
                url_key] = UrlTechnologiesSet(path_entry['Technologies'],
                                              last_full_builtwith_scan=last_full_builtwith_scan)

    def __iter__(self):
        return iter(self._technologies_by_url.values())

    @staticmethod
    def __get_url_key(domain, subdomain, path):
        return domain, subdomain, path

    def available_urls(self):
        return self._technologies_by_url.keys()

    def get_technologies_by_url(self, domain, subdomain, path):
        return self._technologies_by_url.get(self.__get_url_key(domain, subdomain, path), None)

# Example usage:
# V1:
#
# >>> from builtwith import BuiltWith
# >>> bw = BuiltWith(YOUR_API_KEY)
# >>> bw.lookup(URL)
#
# V2:
#
# >>> from builtwith import BuiltWith
# >>> bw = BuiltWith(YOUR_API_KEY, api_version=2)
# >>> bw.lookup(URL)


class BuiltWith(object):
    """
    BuiltWith API version client.
    """

    def __init__(self, key, api_version=1):
        """
        Initialize the client. Requires a BuiltWith API key. Optionally takes in the API version. If no API version is
        specified, a default of `1` is used.
        """

        if api_version not in ENDPOINTS_BY_API_VERSION.keys():
            raise UnsupportedApiVersion(VERSION_EXCEPTION_TEMPLATE % api_version)

        self.key = key
        self.api_version = api_version

    def lookup(self, domain, last_full_query=False):
        """
        Lookup BuiltWith results for the given domain. If API version 2 is used and the last_full_query flag enabled,
        it also queries for the date of the last full BuiltWith scan.
        """

        last_full_builtwith_scan = None

        if self.api_version == 2 and last_full_query:
            last_updates_resp = requests.get(ENDPOINTS_BY_API_VERSION[self.api_version], params={'UPDATE': 1})
            last_updated_data = last_updates_resp.json()
            last_full_builtwith_scan = datetime.datetime.strptime(last_updated_data['FULL'], '%Y-%m-%d').date()

        params = {
            'KEY': self.key,
            'LOOKUP': domain,
        }
        response = requests.get(ENDPOINTS_BY_API_VERSION[self.api_version], params=params)

        if self.api_version == 1:
            return response.json()

        return BuiltWithDomainInfo(response.json(), last_full_builtwith_scan)
