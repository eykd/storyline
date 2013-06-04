# -*- coding: utf-8 -*-
"""storyline.states -- state machines for telling stories.
"""
import re
from collections import defaultdict
import logging

from path import path
from jinja2 import Environment

environment = Environment(
    line_statement_prefix = u'%',
    line_comment_prefix = u'!!',
)

logger = logging.getLogger('storyline')


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

    def __repr__(self):
        return u"<Series: %s>" % self.name


class Situation(object):
    def __init__(self, name):
        self.name = name
        self.content = u''
        self.directives = {}
        self.series = None
        self.prepared = False

    def __repr__(self):
        return u"<Situation: %s>" % self.address

    @property
    def address(self):
        return u'%s::%s' % (self.series.name, self.name)

    @property
    def template(self):
        if not hasattr(self, '_template'):
            self._template = environment.from_string(self.content)
        return self._template

    def prepare(self, state):
        """Return a copy of this Situation with rendered content and reified directives.
        """
        content = self.template.render(**state.context(self.series.plot, self))
        directives, content = self.get_directives(content, state)
        prepared = Situation(self.name)
        prepared.content = content
        prepared.directives = directives
        prepared.series = self.series
        prepared.prepared = True
        return prepared

    link_cp = re.compile(r'\[(?P<text>.+?)\]\((?P<target>.+?)\)', re.MULTILINE)

    def get_directives(self, content, state):
        directives = dict((n, d) for n, d in self.directives.iteritems()
                          if n.startswith('on_'))
        new_content = []
        start = 0
        for match in self.link_cp.finditer(content):
            new_content.append(content[start:match.start()])
            start = match.end()
            text, target = match.groups()
            if target in self.directives:
                # Targets a defined directive.
                new_content.append(match.group())
                directives[target] = self.directives[target]
            else:
                # We need to parse an inline directive.
                if target == '!':
                    if text in directives:
                        pass
                    elif text in self.directives:
                        directives[text] = self.directives[text]
                    else:
                        d = Directive(text, u'')
                        d.situation = self
                        directives[text] = d
                else:
                    action, obj = target.split('!', 1)
                    script = u'{{{{ {action}({obj}) }}}}'.format(
                        action=action,
                        obj=u'"{}"'.format(obj) if obj.strip() else u''
                    )
                    d = Directive(text, script)
                    d.situation = self
                    directives[text] = d
                new_content.append(u'[{text}]({text})'.format(text=text))
        try:
            new_content.append(content[start:])
        except IndexError:
            pass
        return directives, u''.join(new_content)

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
    def __repr__(self):
        return u"<Directive: %s::%s>" % (self.situation.address, self.name)

    def __init__(self, name, content=u''):
        self.name = name
        self.content = content
        self.situation = None

    @property
    def template(self):
        if not hasattr(self, '_template'):
            self._template = environment.from_string(self.content)
        return self._template

    def execute(self, situation, state):
        return self.template.render(**state.context(situation.series.plot, situation))


class Plot(object):
    def __init__(self, *series):
        self.by_name = {}
        self.add_series(*series)
        self.loaded = False

    def add_series(self, *series):
        self.by_name.update((s.name, s) for s in series)
        for s in series:
            s.plot = self

    def load_path(self, p):
        """Load all the series definitions in the given path.
        """
        from .storyfile import StoryParser
        parser = StoryParser()

        p = path(p).expand().abspath()
        for fp in p.walkfiles('*.story'):
            logger.info("Loading %s" % fp)
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
        return u''


class PlotState(object):
    def __init__(self, start=None):
        self.stack = []
        self.situation = None
        self.messages = []
        self.inventory = set()
        self.this = ContextState()
        self.locations = defaultdict(ContextState)

    def __repr__(self):
        return u"<PlotState: %s::%s>" % (u', '.join(self.stack), self.situation)

    @classmethod
    def from_dict(cls, plot, d):
        state = plot.make_state()
        state.stack[:] = d.get('stack', (('start', None), ))
        for n, item in enumerate(state.stack):
            if isinstance(item, basestring):
                state.stack[n] = (item, None)
        state.situation = d.get('situation', None)
        state.inventory = set(d.get('inventory', ()))
        state.this.update(d.get('this', {}))
        state.locations.update(d.get('locations', {}))
        return state

    def to_dict(self):
        return {
            'stack': self.stack,
            'situation': self.situation,
            'inventory': list(self.inventory),
            'this': dict(self.this),
            'locations': dict(self.locations),
        }

    @property
    def top(self):
        return self.stack[-1]

    def context(self, plot, situation):
        return {
            # Local context objects
            'this': self.this,
            'inventory': self.inventory,
            'here': self.locations[situation.address],
            'elsewhere': self.locations,

            # Local context actions
            'push': lambda a: self.push(plot, a) or u'',
            'pop': lambda: self.pop(plot) or u'',
            'replace': lambda a: self.replace(plot, a) or u'',
            'select': lambda a: self.replace(plot, a) or u''
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

    def add_message(self, message, plot=None):
        if message and message.strip():
            self.messages.append(message.rstrip().lstrip(u'\n'))

    def push(self, plot, situation):
        if isinstance(situation, basestring):
            situation = self.parse_address(plot, situation)
        self._exit(plot)
        self.stack.append((situation.series.name, situation.name))
        self._enter(plot, situation, exit=False)

    def pop(self, plot):
        self._exit(plot)
        self.stack.pop()
        if not self.stack:
            self.push(plot, 'start')
        else:
            self._enter(plot)

    def _enter(self, plot, situation=None, exit=True):
        if situation is None:
            series, situation = self.top
        if situation is None:
            situation = self.parse_address(plot, series)
        if isinstance(situation, basestring):
            situation = self.parse_address(plot, situation)
        if not situation.prepared:
            situation = situation.prepare(self)
        if exit:
            self._exit(plot)
        self.situation = (situation.series.name, situation.name)
        self.add_message(situation.trigger(self, 'on_enter'))
        self.add_message(situation.content)

    def _exit(self, plot):
        if self.situation is not None:
            self.add_message(self.current(plot).trigger(self, 'on_exit'))
            self.situation = None

    def replace(self, plot, situation):
        if isinstance(situation, basestring):
            situation = self.parse_address(plot, situation)
        self._exit(plot)
        self.stack[-1] = (situation.series.name, situation.name)
        self._enter(plot, situation, exit=False)

    def current(self, plot):
        try:
            series, situation = self.top
            if situation is not None:
                current = plot.by_name[series].by_name[situation].prepare(self)
            else:
                current = plot.by_name[series].ordered[0].prepare(self)
            return current
        except IndexError:
            return None

    def choose(self, plot, action):
        self.add_message(self.current(plot).trigger(self, action))
