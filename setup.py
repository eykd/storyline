# -*- coding: utf-8 -*-
"""setup.py -- setup file for storyline
"""
import sys
import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

PYVERSION = float('%s.%s' % (sys.version_info[0], sys.version_info[1]))
PATH = os.path.abspath(os.path.dirname(__file__))

INSTALL_REQUIRES = [
    line
    for line in
    open(os.path.join(PATH, 'requirements.txt')).read().splitlines()
    if not line.startswith('-') and not line.startswith('#')
]

TESTS_REQUIRE = [
    line
    for line in
    open(os.path.join(PATH, 'test-requirements.txt')).read().splitlines()
    if not line.startswith('-') and not line.startswith('#')
]

README = os.path.join(PATH, 'README.rst')

SETUP = dict(
    name = "storyline",
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'storyline = storyline.http:main',

        ],
    },
    install_requires = INSTALL_REQUIRES,
    tests_require = TESTS_REQUIRE,
    test_suite = 'nose.collector',

    package_data = {
        '': ['*.txt', '*.html'],
    },
    zip_safe = False,

    version = "0.1",
    description = "A simple, but non-obvious approach to setting boundaries.",
    long_description = open(README).read(),
    author = "David Eyk",
    author_email = "david.eyk@gmail.com",
    url = "http://github.com/eykd/storyline",
    license = 'BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Topic :: Software Development :: Libraries',
        ],
    )

setup(**SETUP)

# -*- coding: utf-8 -*-
"""setup.py -- setup file for Storyline
"""
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

with open('./requirements.txt') as fi:
    REQUIREMENTS = [i.strip() for i in fi.readlines()]


setup(
    name = "storyline",
    version = "0.1",
    install_requires = [
        "Flask==0.10.1",
        "Jinja2==2.7.2",
        "Markdown==2.4",
        "MarkupSafe==0.21",
        "configobj==5.0.4",
        "docopt==0.6.1",
        "msgpack-python==0.4.2",
        "path.py==5.1",
        "smartypants==1.8.3",
        "typogrify==2.0.4",
        "watchdog==0.7.1",
        "webassets==0.9",
    ],
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'storyline = storyline.http:main',

        ],
    },
)
