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

    def test_it_should_get_None_if_no_content(self):
        from storyline import templates

        class MyObject(templates.Renderable):
            content = ""

        obj = MyObject()
        ensure(obj.template).is_none()


    def test_it_should_get_None_if_whitespace_content(self):
        from storyline import templates

        class MyObject(templates.Renderable):
            content = "\n    "

        obj = MyObject()
        ensure(obj.template).is_none()
