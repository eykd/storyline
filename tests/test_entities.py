# -*- coding: utf-8 -*-
"""tests for story factories
"""
import unittest

from ensure import ensure


class SituationEntityTests(unittest.TestCase):
    def setUp(self):
        from storyline import entities
        self.situation = entities.Situation(
            name = 'foo',
            series = 'bar',
            content = '',
            directives = {},
        )

    def test_it_should_have_an_identifying_pair(self):
        ensure(self.situation.pair).equals(('bar', 'foo'))

    def test_it_should_have_an_identifying_address(self):
        ensure(self.situation.address).equals('bar::foo')
