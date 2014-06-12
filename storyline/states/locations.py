# -*- coding: utf-8 -*-
"""storyline.states.locations
"""
from nonobvious import frozendict, fields, V

from ..context import ContextState
from . import base


class LocationState(base.PlotStateEntity):
    locations = fields.Field(
        default = frozendict(),
        validator = V.ChainOf(
            V.Mapping(
                key_schema = 'string',
                value_schema = base.simple_value_frozendict,
            ),
            V.AdaptTo(frozendict),
        )
    )

    def as_context(self, address, commands):
        locations = ContextState(
            (name, ContextState(value))
            for name, value in self.locations.iteritems()
        )

        return {
            'here': locations.get(address, ContextState()),
            'elsewhere': locations,
            'locations': locations,
            'at': locations,
        }

    def from_context(self, context):
        return self.copy(
            locations = context.get('locations', self.locations),
        )

    def reset(self, situation=None):
        return self.copy(
            locations = {},
        )
