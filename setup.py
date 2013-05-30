# -*- coding: utf-8 -*-
"""setup.py -- setup file for Storyline
"""
from setuptools import setup, find_packages

with open('./requirements.txt') as fi:
    REQUIREMENTS = [i.strip() for i in fi.readlines()]


setup(
    name = "storyline",
    version = "0.1",
    install_requires = REQUIREMENTS,
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'storyline = storyline.http:main',

        ],
    },
)
