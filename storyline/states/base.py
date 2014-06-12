# -*- coding: utf-8 -*-
"""storyline.states.base -- state machines for telling stories.
"""
import collections
import logging
import warnings

logger = logging.getLogger('storyline')

from nonobvious import entities, fields
from nonobvious import frozendict, frozenlist, frozenset
from nonobvious import V

from ..contexts import ContextSet, ContextState, ContextList
from .. import plugins
from .. import templates

simple_value_frozendict = V.ChainOf(
    V.Mapping(
        key_schema = 'string',
        value_schema = V.AnyOf(
            'boolean',
            'string',
            'number',
        )
    ),
    V.AdaptTo(frozendict),
)

situation_tuple = V.ChainOf(
    V.HomogeneousSequence(
        item_schema = 'string',
        min_length = 2,
        max_length = 2,
    ),
    V.AdaptTo(tuple),
)


class PlotStateManager(object):
    default_base_states = [
        'storyline.states.stack.StackState',
        'storyline.states.flags.FlagsState',
        'storyline.states.this.ThisState',
        'storyline.states.locations.LocationState',
    ]

    def __init__(self, plot, *args, **kwargs):
        super(PlotStateManager, self).__init__()
        self.plot = plot
        self.messages = []
        base = self.plot.config['states'].get('base') or self.default_base_states
        extensions = self.plot.config['states'].get('extensions') or []
        self.plugins = base + extensions
        self.states = dict(
            (plugin_path, self._get_plugin(plugin_path, *args, **kwargs))
            for plugin_path in base + extensions
        )

    def _get_plugin(self, plugin_path, *args, **kwargs):
        try:
            ext_class = plugins.import_plugin(plugin_path)
        except ImportError as e:
            warnings.warn("Plugin {} is not available: {}".format(plugin_path, e.message))
        return ext_class(self.plot, self.messages, *args, **kwargs)

    def get_events(self, event):
        """Return executable content for the given event.
        """
        for state in self.states.itervalues():
            template = state.get_event(event)
            if template is not None:
                yield template

    def get_contexts(self, commands):
        for state in self.states.itervalues():
            yield state.get_context(commands)

    def render_situation(self):
        return u''

    def clear_messages(self):
        self.messages[:] = ()


class PlotStateEntity(entities.Entity):
    def __init__(self, plot, messages, *args, **kwargs):
        self.plot = plot
        self.messages = messages
        super(PlotStateEntity, self).__init__(*args, **kwargs)

    def copy(self, *args, **kwargs):
        """Return a shallow copy, optionally with updated members as specified.

        Updated members must pass validation.
        """
        return self.__class__(self.plot, self.messages, self, *args, **kwargs)

    def as_context(self, commands):
        return {}

    def from_context(self, context):
        return self

    def add_message(self, message):
        """Add a message to the output buffer.
        """
        if isinstance(message, basestring):
            message = templates.get_template_from_string(message)
        if message is not None:
            logger.debug("New message:\n {}\n".format(message))
            logger.debug("Messages: {}".format(self.messages))
            self.messages.append(message)
        return self

    def get_event(self, action):
        pass


class PlotState(entities.Entity):
    stack = fields.Field(
        default = (),
        validator = V.ChainOf(
            V.HomogeneousSequence(
                item_schema=situation_tuple
            ),
            V.AdaptTo(frozenlist),
        ))
    situation = fields.Field(
        default = None,
        validator = V.AnyOf(
            lambda x: x is None,
            situation_tuple,
        ))
    messages = fields.StringList(default=())
    flags = fields.Field(
        default = (),
        validator = V.ChainOf(
            V.Type(accept_types=(collections.Iterable, )),
            lambda c: all(isinstance(i, basestring) for i in c),
            V.AdaptTo(frozenset),
        )
    )
    this = fields.Field(
        default = frozendict(),
        validator = simple_value_frozendict
    )
    locations = fields.Field(
        default = frozendict(),
        validator = V.ChainOf(
            V.Mapping(
                key_schema = 'string',
                value_schema = simple_value_frozendict,
            ),
            V.AdaptTo(frozendict),
        )
    )

    @property
    def top(self):
        """Return the top situation in the stack.
        """
        try:
            return self.stack[-1]
        except IndexError:
            return None

    def __init__(self, plot, *args, **kwargs):
        self.plot = plot
        super(PlotState, self).__init__(*args, **kwargs)

    def copy(self, *args, **kwargs):
        """Return a shallow copy, optionally with updated members as specified.

        Updated members must pass validation.
        """
        return self.__class__(self.plot, self, *args, **kwargs)

    def as_context(self):
        commands = ContextList()
        situation = situation = self.plot.get_situation_by_address(self.situation)
        flags = ContextSet(self.flags)
        this = ContextState(self.this)
        locations = ContextState(
            (name, ContextState(value))
            for name, value in self.locations.iteritems()
        )

        return {
            # Local context object synonyms
            'this': this,
            'its': this,
            'I': this,
            'my': this,
            'we': this,
            'our': this,
            'he': this,
            'his': this,
            'she': this,

            'here': locations.get(situation.address, ContextState()),
            'elsewhere': locations,

            'flags': flags,
            'commands': commands,

            # Local context actions
            'push': lambda a: commands.append(('push', a)) or u'',
            'pop': lambda a=None: commands.append(('pop', )) or u'',
            'replace': lambda a: commands.append(('replace', a)) or u'',
            'select': lambda a: commands.append(('replace', a)) or u'',
            'reset': lambda a=None: commands.append(('reset', a)) or u''
        }

    valid_commands = set(('push', 'pop', 'replace', 'reset'))

    def from_context(self, context):
        new_state = self.copy(
            this = context.get('this', self.this),
            locations = context.get('locations', self.locations),
            flags = context.get('flags', self.flags),
        )
        for command in context.get('commands', ()):
            method = command[0]
            args = command[1:]
            new_state = getattr(new_state, method)(*args)
        return new_state

    def clear_messages(self):
        """Clear the message output buffer.
        """
        return self.copy(messages=())

    def add_message(self, message):
        """Add a message to the output buffer.
        """
        if message and message.strip():
            message = message.rstrip().lstrip(u'\n')
            logger.debug("New message:\n {}\n".format(message))
            logger.debug("Messages: {}".format(self.messages))
            return self.copy(messages=self.messages+[message])
        else:
            return self

    def trigger(self, directive, *args, **kwargs):
        """Execute the named directive on the current situation.
        """
        ctx = self.as_context()
        message = self._current().trigger(directive, ctx, *args, **kwargs)
        return self.from_context(ctx).add_message(message)

    def render_situation(self):
        ctx = self.as_context()
        message = self._current().render(ctx)
        return self.from_context(ctx).add_message(message)

    def push(self, situation):
        """Push the situation (by address) onto the stack.
        """
        if isinstance(situation, basestring):
            situation = self.plot.get_situation_by_address(situation, self._current())
        new_state = self._exit()
        new_state = new_state.copy(stack = new_state.stack + [situation.pair])
        return new_state._enter(situation, exit=False)

    def pop(self):
        """Pop the current situation off the stack.
        """
        new_state = self._exit()
        new_state = new_state.copy(stack=new_state.stack[:-1])
        if not new_state.stack:
            return new_state.push(self.plot.config['start'])
        else:
            return new_state._enter()

    def replace(self, situation):
        """Replace the current situation on the stick with the named situation.
        """
        if isinstance(situation, basestring):
            situation = self.plot.get_situation_by_address(situation, self._current())
        new_state = self._exit()
        new_state = new_state.copy(stack = new_state.stack[:-1] + [situation.pair])
        return new_state._enter(situation, exit=False)

    def reset(self, situation=None):
        """Clear the stack and start fresh with the named situation.
        """
        if not situation:
            situation = self.plot.config['start']
        if isinstance(situation, basestring):
            situation = self.plot.get_situation_by_address(situation, self._current())
        new_state = self._exit()

        # Clear all state
        new_state = new_state.copy(
            stack = [situation.pair],
            situation = None,
            flags = (),
            this = {},
            locations = {},
        )

        return new_state._enter(situation, exit=False)

    def _enter(self, situation=None, exit=True):
        new_state = self
        if situation is None:
            series, situation = self.top
        if isinstance(situation, basestring):
            situation = self.plot.get_situation_by_address(situation, self._current())
        if exit:
            new_state = self._exit()
        new_state = new_state.copy(situation=situation.pair)
        new_state = new_state.trigger('on_enter')
        new_state = new_state.render_situation()
        return new_state

    def _exit(self):
        if self.situation is not None:
            new_state = self.trigger('on_exit')
            return new_state.copy(situation=None)
        return self

    def _current(self):
        """Return the current situation of the plot.
        """
        top = self.top
        if top is not None:
            return self.plot.get_situation_by_address(self.top)
        else:
            return None
