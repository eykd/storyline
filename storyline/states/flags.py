# -*- coding: utf-8 -*-
"""storyline.states.flags
"""
import collections

from nonobvious import fields, V

from ..context import ContextSet
from . import base


class FlagsState(base.PlotStateEntity):
    flags = fields.Field(
        default = (),
        validator = V.ChainOf(
            V.Type(accept_types=(collections.Iterable, )),
            lambda c: all(isinstance(i, basestring) for i in c),
            V.AdaptTo(frozenset),
        )
    )

    def as_context(self, address, commands):
        return {
            'flags': ContextSet(self.flags)
        }

    def from_context(self, context):
        return self.copy(
            flags = context.get('flags', self.flags),
        )

    def reset(self, situation=None):
        """Clear the stack and start fresh with the named situation.
        """
        return self.copy(
            flags = (),
        )
