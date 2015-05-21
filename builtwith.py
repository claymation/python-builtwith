import copy
import datetime
import re
import requests


ENDPOINTS_BY_API_VERSION = {1: 'http://api.builtwith.com/v1/api.json',
                            2: 'http://api.builtwith.com/v2/api.json',
                            7: 'http://api.builtwith.com/v7/api.json'}

VERSION_EXCEPTION_TEMPLATE = 'Version %s'

DATETIME_INFORMATION_NAMES = ['FirstDetected', 'LastDetected']


class UnsupportedApiVersion(NotImplementedError):
    pass


def _convert_timestamp_to_utc_datetime(timestamp):
    if not isinstance(timestamp, int):
        timestamp = int(re.search('\d+', timestamp).group(0))

    return datetime.datetime.utcfromtimestamp(timestamp / 1000)


class UrlTechnologiesSet(object):

    def __init__(self, technologies_list, last_full_builtwith_scan_date=None):
        """
        Initializes the object using the list of technology dictionaries that are copied and formatted. Takes an
        optional parameter for the datetime.date object of the last full BuiltWith scan.
        """

        self._technologies_by_name = {}

        for technologies_dict in technologies_list:
            copied_technologies_dict = copy.deepcopy(technologies_dict)

            for name in DATETIME_INFORMATION_NAMES:
                copied_technologies_dict[name] = _convert_timestamp_to_utc_datetime(technologies_dict[name])

            # According to the team at BuiltWith, it's best to just use the last "FULL" scan
            # time in the CurrentlyLive determination since BuiltWith doesn't publish their
            # smaller "TOPSITE" list. Downside is that this client will say some technologies were
            # successfully detected on "TOPSITE" sites on the the last BuiltWith scan when that's
            # not in fact accurate.
            if last_full_builtwith_scan_date:
                copied_technologies_dict['CurrentlyLive'] = (
                    last_full_builtwith_scan_date <= copied_technologies_dict['LastDetected'].date())

            self._technologies_by_name[technologies_dict['Name']] = copied_technologies_dict

    def __iter__(self):
        return iter(self._technologies_by_name.values())

    def get_technology_info(self, technology_name):
        return self._technologies_by_name.get(technology_name, None)

    def list_technologies(self):
        return self._technologies_by_name.keys()


class BuiltWithDomainInfo(object):

    def __init__(self, api_response_json, last_full_builtwith_scan_date=None):
        self.api_response_json = api_response_json
        self._technologies_by_url = {}
        for path_entry in api_response_json['Paths']:
            url_key = self.__get_url_key(
                path_entry['Domain'], path_entry.get('SubDomain', None), path_entry['Url'])
            self._technologies_by_url[
                url_key] = UrlTechnologiesSet(path_entry['Technologies'],
                                              last_full_builtwith_scan_date=last_full_builtwith_scan_date)

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
#
# V7:
#
# >>> from builtwith import BuiltWith
# >>> bw = BuiltWith(YOUR_API_KEY, api_version=7)
# >>> bw.lookup(URL)  # look up a single domain
# >>> bw.lookup([URL1, URL2, ..., URL16])  # or look up up to 16 domains at once


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

    def lookup(self, domain, get_last_full_query=True):
        """
        Lookup BuiltWith results for the given domain. If API version 2 is used and the get_last_full_query flag
        enabled, it also queries for the date of the last full BuiltWith scan.
        """

        last_full_builtwith_scan_date = None

        if self.api_version == 7 and isinstance(domain, list):
            domain = ','.join(domain)

        if self.api_version in [2, 7]:
            last_updates_resp = requests.get(ENDPOINTS_BY_API_VERSION[self.api_version], params={'UPDATE': 1})
            last_updated_data = last_updates_resp.json()

            if get_last_full_query and last_updated_data['FULL']:
              last_full_builtwith_scan_date = datetime.datetime.strptime(last_updated_data['FULL'], '%Y-%m-%d').date()

        params = {
            'KEY': self.key,
            'LOOKUP': domain,
        }

        response = requests.get(ENDPOINTS_BY_API_VERSION[self.api_version], params=params)

        if self.api_version == 1:
            return response.json()
        elif self.api_version == 2:
            return BuiltWithDomainInfo(response.json(), last_full_builtwith_scan_date)
        elif self.api_version == 7:
            domain_info = list()
            for result in response.json()['Results']:
                domain_info.append(BuiltWithDomainInfo(result['Result'], last_full_builtwith_scan_date))
            return domain_info
