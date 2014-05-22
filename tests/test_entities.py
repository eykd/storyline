# -*- coding: utf-8 -*-
"""tests for story factories
"""
import unittest

from ensure import ensure
from mock import patch


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

    def test_it_should_trigger_its_directive(self):
        from storyline import entities
        directive = entities.Directive(
            name = 'do it!',
            content = '{% for arg in args %}{{ arg }} {% endfor %}',
        )
        situation = entities.Situation(
            name = 'foo',
            series = 'qux',
            content = '',
            directives = {'do it!': directive}
        )
        ensure(situation.trigger).called_with('do it!', {}, 'foo', 'bar', 'baz').equals("foo bar baz ")

    def test_it_should_warn_when_triggering_nonexistent_directive(self):
        from storyline import entities
        situation = entities.Situation(
            name = 'foo',
            series = 'qux',
            content = '',
            directives = {}
        )

        with patch('warnings.warn') as mock_warnings:
            ensure(situation.trigger).called_with('do it!', {}, 'foo', 'bar', 'baz').equals(None)
            ensure(mock_warnings.call_count).equals(1)



class DirectiveEntityTests(unittest.TestCase):
    def test_it_should_execute_its_content(self):
        from storyline import entities
        directive = entities.Directive(
            name = 'foo',
            content = '{% for arg in args %}{{ arg }} {% endfor %}',
        )
        ensure(directive.execute).called_with({}, 'foo', 'bar', 'baz').equals("foo bar baz ")
