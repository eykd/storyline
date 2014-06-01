# -*- coding: utf-8 -*-
"""tests for configs
"""
import unittest

from ensure import ensure


class LoadConfigTests(unittest.TestCase):
    def test_it_should_load_defaults(self):
        from storyline import defaults
        config = defaults.load_config()
        ensure(config['start']).equals('start')
        ensure(config['markdown']['extensions']).equals([])
