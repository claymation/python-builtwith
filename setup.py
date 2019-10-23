from setuptools import setup

setup(
    name = "python-builtwith",
    version = "0.2.2",
    description = "BuiltWith API versions 1, 2 and 7 client",
    author = "Clay McClure, Jon Gaulding, Andrew Harris",
    author_email = "clay@daemons.net",
    url = "https://github.com/claymation/python-builtwith",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
    ],
    py_modules = ['builtwith'],
    install_requires = [
        'requests==2.20.0',
    ],
    test_suite = 'nose.collector',
    tests_require = [
        'httpretty==0.5.12',
        'nose==1.2.1',
    ]
)
