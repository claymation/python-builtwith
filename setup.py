from setuptools import setup

setup(
    name = "python-builtwith",
    version = "1.0.0",
    description = "BuiltWith API versions 1, 2 and 7 client",
    author = "Clay McClure, Jon Gaulding, Andrew Harris",
    author_email = "clay@daemons.net",
    url = "https://github.com/claymation/python-builtwith",
    classifiers = [
        'Development Status :: 7 - Inactive',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
    ],
    py_modules = ['builtwith'],
    install_requires = [
        'requests',
    ],
    test_suite = 'nose.collector',
    tests_require = [
        'httpretty',
        'nose',
    ]
)
