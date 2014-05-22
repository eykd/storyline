# -*- coding: utf-8 -*-
"""tests for story factories
"""
import unittest

from ensure import ensure
from mock import patch


class PlotEntityTests(unittest.TestCase):
    def setUp(self):
        from storyline import entities
        situations = [
            entities.Situation(name='bar', series='foo'),
            entities.Situation(name='baz', series='foo'),
        ]
        self.plot = entities.Plot(
            by_name = {
                'foo': entities.Series(
                    name = 'foo',
                    content = '',
                    ordered = situations,
                    by_name = dict((s.name, s) for s in situations)
                )
            },
            config = {},
        )

    def test_it_should_parse_absolute_addresses(self):
        ensure(
            self.plot.parse_address("foo::bar")
        ).equals(
            ('foo', 'bar')
        )

    def test_it_should_parse_a_series_address_without_a_current_situation(self):
        ensure(
            self.plot.parse_address("foo")
        ).equals(
            ('foo', None)
        )

    def test_it_should_parse_a_series_address_with_a_current_situation(self):
        current_situation = self.plot.by_name['foo'].by_name['baz']

        ensure(
            self.plot.parse_address("blah", current_situation)
        ).equals(
            ('blah', None)
        )

    def test_it_should_parse_addresses_relative_to_current_situation(self):
        current_situation = self.plot.by_name['foo'].by_name['baz']
        ensure(
            self.plot.parse_address("bar", current_situation)
        ).equals(
            ('foo', 'bar')
        )

    def test_it_should_get_a_situation_by_absolute_address(self):
        ensure(
            self.plot.get_situation_by_address("foo::bar")
        ).is_(
            self.plot.by_name['foo'].by_name['bar']
        )

    def test_it_should_get_a_situation_by_relative_address(self):
        current_situation = self.plot.by_name['foo'].by_name['bar']
        ensure(
            self.plot.get_situation_by_address("baz", current_situation)
        ).is_(
            self.plot.by_name['foo'].by_name['baz']
        )

    def test_it_should_get_a_situation_by_first_in_series(self):
        ensure(
            self.plot.get_situation_by_address("foo")
        ).is_(
            self.plot.by_name['foo'].ordered[0]
        )

        current_situation = self.plot.by_name['foo'].by_name['bar']
        ensure(
            self.plot.get_situation_by_address("foo", current_situation)
        ).is_(
            self.plot.by_name['foo'].ordered[0]
        )


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
