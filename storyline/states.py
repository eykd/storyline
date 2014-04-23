# -*- coding: utf-8 -*-
"""storyline.states -- state machines for telling stories.
"""
import re
import inspect
from collections import defaultdict
import logging
import urllib

from path import path
from jinja2 import Environment

environment = Environment(
    line_statement_prefix = u'%',
    line_comment_prefix = u'!!',
    trim_blocks = True,
    lstrip_blocks = True,
)

logger = logging.getLogger('storyline')


class Series(object):
    """Represent an ordered collection of Situations.

    This collection usually corresponds to a single .story file.
    """
    def __init__(self, name):
        self.name = name
        self.parent = path(name).parent
        self.content = u''
        self.ordered = []
        self.by_name = {}

    def add_situation(self, situation):
        """Add a situation to the Series.
        """
        if self.ordered:
            ps = self.ordered[-1]
            ps.next = situation
            situation.prev = ps
        self.ordered.append(situation)
        self.by_name[situation.name] = situation
        situation.series = self

    def __repr__(self):
        return u"<Series: {}>".format(self.name)


class Situation(object):
    """A story state, with corresponding transition directives.
    """
    def __init__(self, name):
        self.name = name
        self.content = u''
        self.directives = {}
        self.series = None
        self.prepared = False

    def __repr__(self):
        return u"<Situation: {}>".format(self.address)

    @property
    def address(self):
        """Return the canonical string which identifies this situation.
        """
        return u'{0}::{0}'.format(self.pair)

    @property
    def pair(self):
        """Return the canonical 2-tuple which identifies this situation.
        """
        return (self.series.name, self.name)

    @property
    def template(self):
        """Return the Jinja2 template for building the Situation's content.
        """
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
        """Identify and parse directives from Markdown links in the given content.

        Return a 2-tuple of a Directives dict and transformed content which
        properly address the directives in the dict.
        """
        directives = dict((n, d) for n, d in self.directives.iteritems()
                          if n.startswith('on_'))
        new_content = []
        start = 0
        # Find all links of the form `[anchor text](directive)`:
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
                    # !: Trigger an event of the same name as anchor text
                    if text in directives:
                        pass
                    elif text in self.directives:
                        directives[text] = self.directives[text]
                    else:
                        d = Directive(text, u'')
                        d.situation = self
                        directives[text] = d
                elif target.startswith('!'):
                    # !event: Trigger the event named
                    action = 'trigger'
                    obj = target[1:]
                else:
                    # action!arg: Call the action with the given argument
                    action, obj = target.split('!', 1)
                    script = u'{{{{ {action}({obj}) }}}}'.format(
                        action = action,
                        obj = u'"{}"'.format(obj.strip()) if obj.strip() else u''
                    )
                    d = Directive(text, script)
                    d.situation = self
                    directives[text] = d

                new_content.append(
                    u'[{text}]({url})'.format(
                        text = text,
                        url = urllib.quote_plus(text)
                    ))
        try:
            new_content.append(content[start:])
        except IndexError:
            pass
        return directives, u''.join(new_content)

    def add_directive(self, directive):
        """Add the given directive to the Situation.
        """
        if directive.name in self.directives:
            raise NameError("Directive with name `{}` already defined on `{}`".format(
                directive.name, self.situation.name
            ))
        self.directives[directive.name] = directive
        directive.situation = self

    def trigger(self, state, directive, *args, **kwargs):
        """Trigger the given directive (by name), executing it on the given state.
        """
        try:
            return self.directives[directive].execute(self, state, *args, **kwargs)
        except KeyError:
            pass


class Directive(object):
    """An event that may be triggered in a Situation.

    Directives has content that may or may not include side-effects.
    """
    def __repr__(self):
        return u"<Directive: {}::{}>".format(self.situation.address, self.name)

    def __init__(self, name, content=u''):
        self.name = name
        self.content = content
        self.situation = None

    @property
    def template(self):
        """Return the Jinja2 template for building the Situation's content.
        """
        if not hasattr(self, '_template'):
            self._template = environment.from_string(self.content)
        return self._template

    def execute(self, situation, state, *args, **kwargs):
        """Execute the directive within the given situation and state.
        """
        context = state.context(situation.series.plot, situation)
        context['args'] = args
        context['kwargs'] = kwargs
        return self.template.render(**state.context(situation.series.plot, situation))


class Plot(object):
    """The Plot manages all Series and manufactures state for the current story.
    """
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
            logger.info("Loading {}".format(fp))
            name = unicode(fp.relpath(p).splitext()[0])
            self.add_series(parser.parse(name, fp.text()))

    def make_state(self, push=True):
        state = PlotState()
        if push:
            state.push(self, 'start')
        return state


class ContextMixin(object):
    """Mixin for data structures used within template contexts.

    Wraps methods on the object to return the empty string instead of None.
    """
    def __getattribute__(self, name):
        """Coerce methods that return None to return the empty string.
        """
        value = object.__getattribute__(self, name)
        if inspect.isbuiltin(value) and hasattr(value, '__call__'):
            def wrapper(*args, **kwargs):
                result = value(*args, **kwargs)
                if result is None:
                    return u''
                else:
                    return result
            return wrapper
        else:
            return value


class ContextState(ContextMixin, dict):
    """A context-ready dict with superpowers.
    """
    def set(self, key, value):
        self[key] = value
        return u''

    def am(self, key, value=None):
        if value is None:
            return self[key]
        else:
            return self.set(key, value)

    are = am

    def incr(self, key, value=1):
        """Increment a numeric value.
        """
        try:
            self[key] += value
        except TypeError:
            raise TypeError('Tried to increment non-numeric key {!r} ({!r}) by {}'.format(
                key, self[key], value
            ))
        except KeyError:
            self[key] = value

        return u''

    def decr(self, key, value=1):
        """Decrement a numeric value.
        """
        try:
            self[key] -= value
        except TypeError:
            raise TypeError('Tried to derement non-numeric key {!r} ({!r}) by {}'.format(
                key, self[key], value
            ))
        except KeyError:
            self[key] = -value

        return u''


class ContextSet(ContextMixin, set):
    """A context-ready set.
    """
    pass


class PlotState(object):
    """The master state object for a current story.
    """
    def __init__(self, start=None):
        self.stack = []
        self.situation = None
        self.messages = []
        self.flags = ContextSet()
        self.this = ContextState()
        self.locations = defaultdict(ContextState)

    def __repr__(self):
        return u"<PlotState: {}::{}>".format(u', '.join(self.stack), self.situation)

    @classmethod
    def from_dict(cls, plot, d=None):
        """Restore state from a dict (usually created by `.to_dict()`).
        """
        logger.debug("Creating PlotState from {}".format(d))
        state = plot.make_state(push=(not d))
        state.stack[:] = d.get('stack', (('start', None), ))
        for n, item in enumerate(state.stack):
            if isinstance(item, basestring):
                state.stack[n] = (item, None)
        state.situation = d.get('situation', None)
        state.flags = ContextSet(d.get('flags', ()))
        state.this.update(d.get('this', {}))
        state.locations.update(d.get('locations', {}))
        return state

    def to_dict(self):
        """Boil the current state down to simple data structures.
        """
        return {
            'stack': self.stack,
            'situation': self.situation,
            'flags': list(self.flags),
            'this': dict(self.this),
            'locations': dict(self.locations),
        }

    @property
    def top(self):
        """Return the top situation in the stack.
        """
        return self.stack[-1]

    def context(self, plot, situation):
        """Return template context based on the current state.
        """
        return {
            # Local context objects
            'this': self.this,
            'I': self.this,
            'my': self.this,
            'we': self.this,
            'our': self.this,

            'flags': self.flags,
            'here': self.locations[situation.address],
            'elsewhere': self.locations,

            # Local context actions
            'push': lambda a: self.push(plot, a) or u'',
            'pop': lambda: self.pop(plot) or u'',
            'replace': lambda a: self.replace(plot, a) or u'',
            'select': lambda a: self.replace(plot, a) or u'',
            'reset': lambda a=None: self.reset(plot, a) or u''
        }

    def get_situation_by_address(self, plot, address):
        """Return the situation identified by the address.

        Addresses take the form of `series::situation`.
        """
        current_series = None
        current_situation = self.current(plot)
        if '::' in address:
            series_name, situation_name = address.split(u'::')
        else:
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

        if series_name not in plot.by_name and current_series is not None:
            series_name = unicode(current_series.parent / series_name)
        series = plot.by_name[series_name]
        return series.by_name[situation_name] if situation_name else series.ordered[0]

    def clear_messages(self, plot=None):
        """Clear the message output buffer.
        """
        self.messages[:] = ()

    def add_message(self, message, plot=None):
        """Add a message to the output buffer.
        """
        if message and message.strip():
            message = message.rstrip().lstrip(u'\n')
            logger.debug("New message:\n {}\n".format(message))
            self.messages.append(message)
            logger.debug("Messages: {}".format(self.messages))

    def trigger(self, plot, directive, *args, **kwargs):
        """Execute the named directive on the current situation.
        """
        return self.current(plot).trigger(self, directive, *args, **kwargs)

    def push(self, plot, situation):
        """Push the situation (by address) onto the stack.
        """
        if isinstance(situation, basestring):
            situation = self.get_situation_by_address(plot, situation)
        self._exit(plot)
        self.stack.append(situation.pair)
        self._enter(plot, situation, exit=False)

    def pop(self, plot):
        """Pop the current situation off the stack.
        """
        self._exit(plot)
        self.stack.pop()
        if not self.stack:
            self.push(plot, 'start')
        else:
            self._enter(plot)

    def replace(self, plot, situation):
        """Replace the current situation on the stick with the named situation.
        """
        if isinstance(situation, basestring):
            situation = self.get_situation_by_address(plot, situation)
        self._exit(plot)
        self.stack[-1] = situation.pair
        self._enter(plot, situation, exit=False)

    def reset(self, plot, situation=None):
        """Clear the stack and start fresh with the named situation.
        """
        if situation is None:
            situation = 'start'
        if isinstance(situation, basestring):
            situation = self.get_situation_by_address(plot, situation)
        self._exit(plot)

        # Clear all state
        self.stack[:] = (situation.pair, )
        self.situation = None
        self.flags.clear()
        self.this.clear()
        self.locations.clear()

        self._enter(plot, situation, exit=False)

    def _enter(self, plot, situation=None, exit=True):
        if situation is None:
            series, situation = self.top
        if situation is None:
            situation = self.get_situation_by_address(plot, series)
        if isinstance(situation, basestring):
            situation = self.get_situation_by_address(plot, situation)
        if not situation.prepared:
            situation = situation.prepare(self)
        if exit:
            self._exit(plot)
        self.situation = situation.pair
        self.trigger(plot, 'on_enter')
        self.add_message(situation.content)

    def _exit(self, plot):
        if self.situation is not None:
            self.trigger(plot, 'on_exit')
            self.situation = None

    def current(self, plot):
        """Return the current situation of the plot.
        """
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
        """Choose (and trigger) the named action directive.

        Really just a synonym for `trigger()`.
        """
        self.trigger(plot, action)
