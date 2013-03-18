python-builtwith
================

[BuiltWith][] API version 1 client.

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
