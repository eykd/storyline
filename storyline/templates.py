# -*- coding: utf-8 -*-
"""storyline.templates
"""
from jinja2 import Environment


environment = Environment(
    line_statement_prefix = u'%',
    line_comment_prefix = u'!!',
    trim_blocks = True,
    lstrip_blocks = True,
)


def get_template_from_string(string):
    return environment.from_string(string)


class Renderable(object):
    @property
    def template(self):
        """Return the Jinja2 template for building the Situation's content.
        """
        if not hasattr(self, '_template'):
            self._template = get_template_from_string(self.content)
        return self._template

    def render(self, context):
        return self.template.render(**context)
