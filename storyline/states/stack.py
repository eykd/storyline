# -*- coding: utf-8 -*-
"""states.stack
"""
import collections
import logging
import warnings

logger = logging.getLogger('storyline')

from nonobvious import fields
from nonobvious import frozenlist
from nonobvious import V

from . import base


situation_tuple = V.ChainOf(
    V.HomogeneousSequence(
        item_schema = 'string',
        min_length = 2,
        max_length = 2,
    ),
    V.AdaptTo(tuple),
)


class StackState(base.PlotStateEntity):
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

    def as_context(self, commands):
        return {
            # Local context actions
            'push': lambda a: commands.append(('push', a)) or u'',
            'pop': lambda a=None: commands.append(('pop', )) or u'',
            'replace': lambda a: commands.append(('replace', a)) or u'',
            'select': lambda a: commands.append(('replace', a)) or u'',
            'reset': lambda a=None: commands.append(('reset', a)) or u''
        }

    @property
    def top(self):
        """Return the top situation in the stack.
        """
        try:
            return self.stack[-1]
        except IndexError:
            return None

    def get_event(self, event):
        """Return executable template for the named directive on the current situation.
        """
        return self._current().get_event(event)

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

    def reset(self):
        new_state = self._exit()

        return new_state.copy(
            stack = [],
            situation = None,
        )

    def _enter(self, situation=None, exit=True):
        new_state = self
        if situation is None:
            series, situation = self.top
        if isinstance(situation, basestring):
            situation = self.plot.get_situation_by_address(situation, self._current())
        if exit:
            new_state = self._exit()
        new_state = new_state.copy(situation=situation.pair)
        new_state.add_message(self.get_event('on_enter'))
        new_state.add_message(self._current().content)
        return new_state

    def _exit(self):
        if self.situation is not None:
            self.add_message(self.get_event('on_exit'))
            return self.copy(situation=None)
        else:
            return self

    def _current(self):
        """Return the current situation of the plot.
        """
        top = self.top
        if top is not None:
            return self.plot.get_situation_by_address(self.top)
        else:
            return None
