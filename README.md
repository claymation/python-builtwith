python-builtwith
================

[BuiltWith][] API versions 1 and 2 client.

    >>> from builtwith import BuiltWith
    >>> bw = BuiltWith(YOUR_API_KEY)
    >>> bw.lookup('example.com')
    {
        'Domain': 'example.com',
        'FullUrl': 'example.com',
        'ProfileUrl': 'http://builtwith.com?example.com',
        'Technologies': [...],
        'Title': ''
    }
    >>>
    >>> bw = BuiltWith(YOUR_API_KEY, api_version=2)
    >>> example_info = bw.lookup('example.com')
    >>> example_info.available_urls()
    [(u'example.com', u'', u'')]
    >>>
    >>> domain_technologies = example_info.get_technologies_by_url(domain="example.com", subdomain="", path="")
    >>> domain_technologies.list_technologies()
    [u'Viewport Meta', u'CentOS', u'Cascading Style Sheets', u'Javascript', u'SEO_TITLE', u'SEO_H1',
     u'XHTML Transitional', u'HTML5 DocType', u'Apache', u'Prototype', u'HTML 4.01 Transitional DTD', u'UTF-8']
    >>>
    >>> domain_technologies.get_technology_info("Prototype")
    {u'Name': u'Prototype', u'FirstDetected': datetime.datetime(2011, 1, 31, 5, 0), u'Tag': u'javascript',
     u'Link': u'http://www.prototypejs.org', u'LastDetected': datetime.datetime(2012, 11, 1, 6, 0),
     u'Description': u'Prototype is a javascript framework which aims to ease development of dynamic web applications.'}
    
[BuiltWith]: http://api.builtwith.com/
