# -*- coding: utf-8 -*-
"""storyline.states -- state machines for telling stories.
"""
import re
from collections import defaultdict
from path import path
from jinja2 import Template


class Series(object):
    def __init__(self, name):
        self.name = name
        self.content = u''
        self.ordered = []
        self.by_name = {}

    def add_situation(self, situation):
        if self.ordered:
            ps = self.ordered[-1]
            ps.next = situation
            situation.prev = ps
        self.ordered.append(situation)
        self.by_name[situation.name] = situation
        situation.series = self


class Situation(object):
    def __init__(self, name):
        self.name = name
        self._content = u''
        self.directives = {}
        self.parsed_directives = {}
        self.series = None

    @property
    def address(self):
        return u'%s::%s' % (self.series.name, self.name)

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = self._parse_directives(value)

    link_cp = re.compile(r'\[(?P<text>.+?)\]\((?P<target>.+?)\)', re.MULTILINE)

    def _parse_directives(self, content):
        new_content = []
        start = 0
        for match in self.link_cp.finditer(content):
            new_content.append(content[start:match.start()])
            start = match.end()
            text, target = match.groups()
            if target in self.directives:
                # Targets a defined directive.
                new_content.append(match.group())
            else:
                # We need to parse an inline directive.
                if target != '!':
                    action, obj = target.split('!', 1)
                    script = u'{{{{ {action}({obj}) }}}}'.format(
                        action=action,
                        obj=u'"{}"'.format(obj) if obj.strip() else u''
                    )
                    self.add_directive(Directive(text, script))
                new_content.append(u'[{text}]({text})'.format(text=text))
        try:
            new_content.append(content[start:])
        except IndexError:
            pass

        return u''.join(new_content)

    def add_directive(self, directive):
        if directive.name in self.directives:
            raise NameError("Directive with name `%s` already defined on `%s`" % (
                directive.name, self.situation.name
            ))
        self.directives[directive.name] = directive
        directive.situation = self

    def trigger(self, state, directive):
        try:
            return self.directives[directive].execute(self, state)
        except KeyError:
            pass


class Directive(object):
    def __init__(self, name, content=u''):
        self.name = name
        self.content = content
        self.situation = None

    @property
    def template(self):
        if not hasattr(self, '_template'):
            self._template = Template(self.content)
        return self._template

    def execute(self, situation, state):
        return self.template.render(**state.context(situation.series.plot, situation))


class Plot(object):
    def __init__(self, *series):
        self.by_name = {}
        self.add_series(*series)

    def add_series(self, *series):
        self.by_name.update((s.name, s) for s in series)
        for s in series:
            s.plot = self

    def load_path(self, p):
        """Load all the series definitions in the given path.
        """
        from .storyfile import StoryParser
        parser = StoryParser()

        p = path(p)
        for fp in p.walkfiles('*.story'):
            name = unicode(fp.relpath(p).splitext()[0])
            self.add_series(parser.parse(name, fp.text()))

    def make_state(self):
        state = PlotState()
        state.push(self, 'start')
        return state


class ContextState(dict):
    def __init__(self):
        pass

    def set(self, key, value):
        self[key] = value


class PlotState(object):
    def __init__(self, start=None):
        self.stack = []
        self.situation = None
        self.messages = []
        self.this = ContextState()
        self.here = defaultdict(ContextState)

    def context(self, plot, situation):
        return {
            'this': self.this,
            'here': self.here[situation.address],
            'push': lambda a: self.push(plot, a) or u'',
            'replace': lambda a: self.replace(plot, a) or u'',
            'select': lambda a: self.enter(plot, a) or u''
        }

    def parse_address(self, plot, address):
        if '::' in address:
            series_name, situation_name = address.split(u'::')
        else:
            current_situation = self.current(plot)
            if current_situation is None:
                # Must be a straight up series name.
                series_name = address
                situation_name = None
            else:
                # Is it a situation name in the current series or a series name?
                current_series = current_situation.series
                if address in current_series.by_name:
                    series_name = current_series.name
                    situation_name = address
                else:
                    series_name = address
                    situation_name = None
        series = plot.by_name[series_name]
        return series.by_name[situation_name] if situation_name else series.ordered[0]

    def clear(self, plot=None):
        self.messages[:] = ()

    def push(self, plot, situation):
        if isinstance(situation, basestring):
            situation = self.parse_address(plot, situation)
        self.exit(plot)
        self.stack.append(situation.series.name)
        self.enter(plot, situation, exit=False)

    def enter(self, plot, situation, exit=True):
        if isinstance(situation, basestring):
            situation = self.parse_address(plot, situation)
        if exit:
            self.exit(plot)
        self.situation = situation.name
        self.messages.append(situation.trigger(self, 'on_enter'))

    def exit(self, plot):
        if self.situation is not None:
            self.messages.append(self.current(plot).trigger(self, 'on_exit'))
            self.situation = None

    def replace(self, plot, situation):
        if isinstance(situation, basestring):
            situation = self.parse_address(plot, situation)
        self.exit(plot)
        self.stack[-1] = situation.series.name
        self.enter(plot, situation, exit=False)

    def current(self, plot):
        try:
            return plot.by_name[self.stack[-1]].by_name[self.situation]
        except IndexError:
            return None

    def choose(self, plot, action):
        self.messages.append(self.current(plot).trigger(self, action))
