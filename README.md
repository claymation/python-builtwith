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
    
[BuiltWith]: http://api.builtwith.com/
