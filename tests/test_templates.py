# -*- coding: utf-8 -*-
"""tests for templates and renderable objects
"""
import unittest

from ensure import ensure

import jinja2


class RenderableTests(unittest.TestCase):
    def test_it_should_get_a_template(self):
        from storyline import templates

        class MyObject(templates.Renderable):
            content = "foo bar"

        obj = MyObject()
        ensure(obj.template).is_a(jinja2.Template)

    def test_it_should_render_a_template(self):
        from storyline import templates

        class MyObject(templates.Renderable):
            content = "foo bar {{ what }}"

        obj = MyObject()
        ensure(obj.render).called_with({'what': 'baz'}).equals('foo bar baz')
