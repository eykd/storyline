# -*- coding: utf-8 -*-
"""storyline.entities
"""
import warnings

from nonobvious import entities, fields, V
from configobj import ConfigObj

from . import templates


class Directive(entities.Entity, templates.Renderable):
    """An event that may be triggered in a Situation.

    Directives has content that may or may not include side-effects.
    """
    name = fields.String()
    situation = fields.String()
    content = fields.String()

    def execute(self, context, *args, **kwargs):
        """Execute the directive within the given situation and state.
        """
        ctx = dict(context)
        ctx['args'] = args
        ctx['kwargs'] = kwargs
        return self.render(ctx)


class Situation(entities.Entity, templates.Renderable):
    """A story state, with corresponding transition directives.
    """
    name = fields.String()
    series = fields.String()
    content = fields.String()
    directives = fields.Field(
        validator=V.Mapping(
            key_schema='string',
            value_schema=V.AdaptTo(Directive)
        ))

    @property
    def address(self):
        """Return the canonical string which identifies this situation.
        """
        return u'{}::{}'.format(*self.pair)

    @property
    def pair(self):
        """Return the canonical 2-tuple which identifies this situation.
        """
        return (self.series, self.name)

    def trigger(self, directive, context, *args, **kwargs):
        """Trigger the given directive (by name), executing it in the given context.
        """
        try:
            return self.directives[directive].execute(context, *args, **kwargs)
        except KeyError:
            warnings.warn("Attempted to trigger a non-existent directive {}".format(directive))


class Series(entities.Entity, templates.Renderable):
    """Represent an ordered collection of Situations.

    This collection usually corresponds to a single .story file.
    """
    name = fields.String()
    content = fields.String()
    ordered = fields.Field(
        validator=V.HomogeneousSequence(
            item_schema=V.AdaptTo(Situation),
        ))
    by_name = fields.Field(
        validator=V.Mapping(
            key_schema='string',
            value_schema=V.AdaptTo(Situation),
        ))


class Plot(entities.Entity):
    """Represent a collection of Series.

    This collection corresponds to all the story files in a projec.
    """
    by_name = fields.Field(
        validator=V.Mapping(
            key_schema='string',
            value_schema=V.AdaptTo(Series),
        ))
    config = fields.Field(validator=V.AdaptTo(ConfigObj))

    def parse_address(self, address, current_situation=None):
        """Parse the given address into series/situation pair.

        Addresses take the form of `series::situation`, `series`, or
        `situation` relative to the given current situation.

        """
        if '::' in address:
            series_name, situation_name = address.rsplit(u'::', 1)
        else:
            if current_situation is None:
                # Must be a straight up series name.
                series_name = address
                situation_name = None
            else:
                # Is it a situation name in the current series or a series name?
                current_series = self.by_name[current_situation.series]
                if address in current_series.by_name:
                    series_name = current_series.name
                    situation_name = address
                else:
                    series_name = address
                    situation_name = None

        return series_name, situation_name

    def get_situation_by_address(self, address, current_situation=None):
        """Return the situation identified by the address.

        Address may be a valid address (see `parse_address`, above) or a
        2-tuple of `(series_name, situation_name)`.

        """
        if isinstance(address, basestring):
            series_name, situation_name = self.parse_address(address, current_situation)
        else:
            # It better be a 2-tuple!
            series_name, situation_name = address

        series = self.by_name[series_name]
        return series.by_name[situation_name] if situation_name else series.ordered[0]
