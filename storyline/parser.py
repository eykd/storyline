# -*- coding: utf-8 -*-
"""storyline.parser -- parser for the storyfile format.
"""
import warnings
import logging
logger = logging.getLogger('storyline.parser')

from . import factories


class StoryParser(object):
    event_map = {
        '# =': 'new_section',
        '# %': 'comment',
        '## %': 'comment',
        '## >': 'directive',
    }

    def parse(self, state, name, storydef):
        state.add_series(name)
        for line in storydef.splitlines():
            self.parse_line(state, line)

    def parse_line(self, state, line):
        for key in self.event_map:
            if line.startswith(key):
                handler = getattr(self, 'on_' + self.event_map[key])
                handler(state, line)
                break
        else:
            self.on_line(state, line)

    def on_line(self, state, line):
        state.add_line(line)

    def on_new_section(self, state, line):
        name = line.split('=', 1)[1].strip()
        state.add_situation(name)

    def on_directive(self, state, line):
        name = line.split('>', 1)[1].strip()
        state.add_directive(name)

    def on_comment(self, state, line):
        # No-op: just a source comment.
        pass


class ParserState(object):
    def __init__(self):
        self.plot = factories.PlotFactory()
        self.series = None
        self.situation = None
        self.directive = None
        self.buffer = []
        self.factories = []

    def add_line(self, line):
        self.factories[-1].add_line(line)

    def pop_all(self):
        self.pop_all_but()

    def pop_all_but(self, *not_kinds):
        factories = self.factories
        while factories and factories[-1].kind not in not_kinds:
            f = factories.pop()
            setattr(self, f.kind, f)

    def add_series(self, name):
        self.pop_all()
        series = self.series = self.plot.add_series(name)
        return series

    def add_situation(self, name):
        self.pop_all_but('series')
        self.situation = s = self.series.add_situation(name)
        self.factories.append(s)
        return s

    def add_directive(self, name):
        self.pop_all_but('series', 'situation')
        if self.situation is None:
            warnings.warn("Encountered a directive (`## > %s`) outside the context of a situation. It will be ignored." % name)
            return

        d = self.situation.add_directive(name)
        self.factories.append(d)
        self.directive = d
        return d

    def compile(self, config=None):
        """Return the compiled plot.
        """
        if config is None:
            self.plot.add_config(config)
        return self.plot.build()
