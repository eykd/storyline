# -*- coding: utf-8 -*-
"""tests for story factories
"""
import unittest

from ensure import ensure


class PlotFactoryTests(unittest.TestCase):
    def setUp(self):
        from storyline import factories
        self.factory = factories.PlotFactory()

    def test_add_series_returns_series_and_extends_plot_series(self):
        from storyline import factories
        series = self.factory.add_series("foo")
        ensure(series).is_a(factories.SeriesFactory)
        ensure(series.name).equals("foo")
        ensure(self.factory.series).has_length(1)
        ensure(self.factory.series[0]).is_(series)

    def test_it_should_build_a_plot_entity(self):
        from storyline import entities
        series = self.factory.add_series("foo")
        series.add_line("blah")
        plot = self.factory.build()
        ensure(plot).is_a(entities.Plot)
        ensure(plot.by_name).has_length(1)
        ensure(plot.by_name['foo']).equals(series.build())
        ensure(plot.config['start']).equals('start')
        ensure(plot.config['markdown']['extensions']).equals([])

    def test_add_config_should_merge_config_objects(self):
        self.factory.add_config({'start': 'intro'})
        plot = self.factory.build()
        ensure(plot.config['start']).equals('intro')
        ensure(plot.config['markdown']['extensions']).equals([])


class SeriesFactoryTests(unittest.TestCase):
    def setUp(self):
        from storyline import factories
        self.factory = factory = factories.SeriesFactory("foo")
        ensure(factory.name).equals("foo")

    def test_add_situation_returns_situation_and_extends_series_situations(self):
        from storyline import factories
        situation = self.factory.add_situation("foo")
        ensure(situation).is_a(factories.SituationFactory)
        ensure(situation.name).equals("foo")
        ensure(self.factory.situations).has_length(1)
        ensure(self.factory.situations[0]).is_(situation)

    def test_add_line_extends_content_lines_and_rstrips_lines(self):
        ensure(self.factory.lines).has_length(0)
        self.factory.add_line("foo bar   ")
        ensure(self.factory.lines).has_length(1)
        self.factory.add_line("bar foo         ")
        ensure(self.factory.lines).has_length(2)
        ensure(self.factory.lines).equals(["foo bar", "bar foo"])

    def test_it_should_build_a_series_entity(self):
        from storyline import entities
        self.factory.add_line("blah boo   ")
        self.factory.add_line("bar foo   ")
        situation = self.factory.add_situation("foo")
        situation.add_line("blah")
        series = self.factory.build()
        ensure(series).is_a(entities.Series)
        ensure(series.name).equals("foo")
        ensure(series.content).equals("blah boo\nbar foo")
        ensure(series.by_name).has_length(1)
        ensure(series.ordered).has_length(1)
        ensure(series.by_name['foo']).is_(series.ordered[0])


class SituationFactoryTests(unittest.TestCase):
    def setUp(self):
        from storyline import factories
        self.factory = factory = factories.SituationFactory("foo", "myseries")
        ensure(factory.name).equals("foo")

    def test_add_directive_returns_directive_and_extends_situation_directives(self):
        from storyline import factories
        directive = self.factory.add_directive("foo")
        ensure(directive).is_a(factories.DirectiveFactory)
        ensure(directive.name).equals("foo")
        ensure(directive.situation_name).equals(self.factory.name)
        ensure(self.factory.directives).has_length(1)
        ensure(self.factory.directives[0]).is_(directive)

    def test_it_should_build_a_situation_entity(self):
        from storyline import entities
        self.factory.add_line("blah boo   ")
        self.factory.add_line("bar foo   ")
        directive = self.factory.add_directive("foo")
        directive.add_line("blah")
        situation = self.factory.build()
        ensure(situation).is_a(entities.Situation)
        ensure(situation.name).equals("foo")
        ensure(situation.series).equals("myseries")
        ensure(situation.content).equals("blah boo\nbar foo")
        ensure(situation.directives).has_length(1)
        ensure(situation.directives['foo']).is_an(entities.Directive)
        ensure(situation.directives['foo']).equals({
            'name': 'foo',
            'situation': situation.name,
            'content': 'blah',
        })


class DirectiveFactoryTests(unittest.TestCase):
    def setUp(self):
        from storyline import factories
        self.factory = factory = factories.DirectiveFactory("foo", "bar")
        ensure(factory.name).equals("foo")
        ensure(factory.situation_name).equals("bar")

    def test_it_should_build_a_directive_entity(self):
        from storyline import entities
        self.factory.add_line("blah boo   ")
        self.factory.add_line("bar foo   ")
        directive = self.factory.build()
        ensure(directive).is_an(entities.Directive)
        ensure(directive.name).equals("foo")
        ensure(directive.situation).equals("bar")
        ensure(directive.content).equals("blah boo\nbar foo")
