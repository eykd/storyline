# -*- coding: utf-8 -*-
"""tests for parsers.
"""
import unittest

from mock import Mock, patch
from ensure import ensure


class ParserStateTests(unittest.TestCase):
    def setUp(self):
        from storyline import parser
        self.state = parser.ParserState()

    def test_add_line_sends_line_to_top_of_stack(self):
        mock = Mock()
        self.state.factories.append(mock)
        self.state.add_line('foo bar')
        mock.add_line.assert_called_with('foo bar')

    def test_add_series_adds_series_to_plot(self):
        mock = Mock()
        self.state.plot = mock
        self.state.add_series('foo')
        mock.add_series.assert_called_with('foo')

    def test_add_series_returns_series_factory(self):
        from storyline import factories
        series = self.state.add_series('foo')
        ensure(series).is_a(factories.SeriesFactory)
        ensure(self.state.series).is_(series)

    def test_add_situation_adds_situation_to_series(self):
        mock = Mock()
        self.state.series = mock
        self.state.add_situation('foo')
        mock.add_situation.assert_called_with('foo')

    def test_add_situation_returns_situation_factory(self):
        from storyline import factories
        self.state.add_series('foo')
        situation = self.state.add_situation('bar')
        ensure(situation).is_a(factories.SituationFactory)
        ensure(self.state.situation).is_(situation)

    def test_add_directive_adds_directive_to_situation(self):
        mock = Mock()
        self.state.situation = mock
        self.state.add_directive('foo')
        mock.add_directive.assert_called_with('foo')

    def test_add_directive_returns_directive_factory(self):
        from storyline import factories
        self.state.add_series('foo')
        self.state.add_situation('foo')
        directive = self.state.add_directive('bar')
        ensure(directive).is_a(factories.DirectiveFactory)
        ensure(self.state.directive).is_(directive)

    def test_add_directive_without_situation_returns_none_and_warns(self):
        self.state.add_series('foo')
        with patch('warnings.warn') as mock_warnings:
            directive = self.state.add_directive('bar')
            ensure(mock_warnings.call_count).equals(1)
        ensure(directive).is_none()

    def test_it_should_compile_the_plot(self):
        from storyline import entities
        plot = self.state.compile()
        ensure(plot).is_an(entities.Plot)
