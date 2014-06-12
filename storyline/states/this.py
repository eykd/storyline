# -*- coding: utf-8 -*-
"""storyline.states.this
"""
from nonobvious import fields, frozendict

from ..context import ContextState
from . import base


class ThisState(base.PlotStateEntity):
    this = fields.Field(
        default = frozendict(),
        validator = base.simple_value_frozendict
    )

    def as_context(self):
        this = ContextState(self.this)

        return {
            # Local context object synonyms
            'this': this,
            'its': this,
            'it': this,
            'I': this,
            'my': this,
            'we': this,
            'our': this,
            'he': this,
            'his': this,
            'she': this,
        }

    def from_context(self, context):
        return self.copy(
            this = context.get('this', self.this),
        )

    def reset(self, situation=None):
        return self.copy(
            this = {},
        )
