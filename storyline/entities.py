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
