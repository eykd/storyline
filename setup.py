# -*- coding: utf-8 -*-
"""setup.py -- setup file for Storyline
"""
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
