# -*- coding: utf-8 -*-
"""test helpers
"""
import unittest
from ensure import ensure
import jinja2


class StateTests(unittest.TestCase):
    def ex_template(self, tmpl):
        return u''.join(tmpl.stream())

    def ex_messages(self, messages):
        ensure(messages).is_an_iterable_of(jinja2.Template)
        return [self.ex_template(t) for t in messages]

    def setUp(self):
        from storyline import entities
        situations = [
            entities.Situation(
                name='bar', series='foo', content="Hello, bar!",
                directives={
                    'on_enter': entities.Directive(name='on_exit', situation='bar', content="Enter bar!"),
                    'on_exit': entities.Directive(name='on_exit', situation='bar', content="Exit bar!"),
                }
            ),
            entities.Situation(
                name='baz', series='foo', content="Hello, baz!",
                directives={
                    'on_enter': entities.Directive(name='on_exit', situation='bar', content="Enter baz!"),
                    'on_exit': entities.Directive(name='on_exit', situation='bar', content="Exit baz!"),
                }
            ),

            entities.Situation(
                name='start', series='foo', content="Hello, start!",
                directives={
                    'on_enter': entities.Directive(name='on_exit', situation='start', content="Enter start!"),
                    'on_exit': entities.Directive(name='on_exit', situation='start', content="Exit start!"),
                }
            ),
        ]
        self.plot = entities.Plot(
            by_name = {
                'foo': entities.Series(
                    name = 'foo',
                    content = '',
                    ordered = situations,
                    by_name = dict((s.name, s) for s in situations)
                )
            },
            config = {
                'start': 'foo::start'
            },
        )

        super(StateTests, self).setUp()
