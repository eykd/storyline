# -*- coding: utf-8 -*-
"""storyline.factories

Factories for generating story objects.
"""
from . import entities
from . import defaults
from nonobvious import frozendict, frozenlist


class Factory(object):
    kind = 'factory'

    def __init__(self, name):
        self.name = name
        self.lines = []

    def add_line(self, line):
        self.lines.append(line.rstrip())


class PlotFactory(object):
    kind = 'plot'

    def __init__(self):
        self.series = []
        self.config = defaults.load_config()

    def add_series(self, name):
        factory = SeriesFactory(name)
        self.series.append(factory)
        return factory

    def add_config(self, config):
        self.config.merge(defaults.load_config(config))

    def build(self):
        return entities.Plot(
            by_name = frozendict((s.name, s.build()) for s in self.series),
            config = self.config,
        )


class SeriesFactory(Factory):
    kind = 'series'

    def __init__(self, name):
        super(SeriesFactory, self).__init__(name)
        self.situations = []

    def add_situation(self, name):
        factory = SituationFactory(name, self.name)
        self.situations.append(factory)
        return factory

    def build(self):
        situations = frozenlist(s.build() for s in self.situations)
        return entities.Series(
            name = self.name,
            content = u"\n".join(self.lines),
            by_name = frozendict((s.name, s) for s in situations),
            ordered = situations,
        )


class SituationFactory(Factory):
    kind = 'situation'

    def __init__(self, name, series_name):
        super(SituationFactory, self).__init__(name)
        self.series_name = series_name
        self.directives = []

    def add_directive(self, name):
        factory = DirectiveFactory(name, self.name)
        self.directives.append(factory)
        return factory

    def build(self):
        return entities.Situation(
            name = self.name,
            series = self.series_name,
            content = u"\n".join(self.lines),
            directives = frozendict((d.name, d.build()) for d in self.directives),
        )


class DirectiveFactory(Factory):
    kind = 'directive'

    def __init__(self, name, situation_name):
        super(DirectiveFactory, self).__init__(name)
        self.situation_name = situation_name
        self.directives = []

    def build(self):
        return entities.Directive(
            name = self.name,
            situation = self.situation_name,
            content = u'\n'.join(self.lines),
        )
