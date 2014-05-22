# -*- coding: utf-8 -*-
"""storyline.entities
"""
from nonobvious import entities, fields, V
from configobj import ConfigObj


class Directive(entities.Entity):
    """An event that may be triggered in a Situation.

    Directives has content that may or may not include side-effects.
    """
    name = fields.String()
    situation = fields.String()
    content = fields.String()


class Situation(entities.Entity):
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


class Series(entities.Entity):
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
