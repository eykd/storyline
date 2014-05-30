# -*- coding: utf-8 -*-
"""tests for storyline.serializers
"""
import unittest

from mock import Mock
from ensure import ensure


class StateSerializerTests(unittest.TestCase):
    def test_loads_should_raise_not_implemented(self):
        from storyline import serializers
        ensure(serializers.StateSerializer.loads).called_with(Mock(), Mock()).raises(NotImplementedError)

    def test_dumps_should_raise_not_implemented(self):
        from storyline import serializers
        ensure(serializers.StateSerializer.dumps).called_with(Mock()).raises(NotImplementedError)


class MsgPackStateSerializerTests(unittest.TestCase):
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

        from storyline import states
        self.state_dict = dict(
            stack=[['foo', 'bar']],
            situation=['foo', 'bar'],
            messages=[],
            flags=['blah', 'la'],
            this={
                'exp': 1,
                'flashlight_on': False,
                'name': 'Inigo Montoya',
            },
            locations={
                'foo::bar': {
                    'cake': 1,
                    'fubar': False,
                    'fraggle': 'rocks',
                }
            },
        )
        self.state = states.PlotState(self.plot, **self.state_dict)

    def test_it_should_dump_state(self):
        from storyline import serializers
        sz = serializers.MsgPackStateSerializer
        packed = sz.dumps(self.state)
        import msgpack
        ensure(msgpack.unpackb(packed)).equals(self.state_dict)

    def test_it_should_load_state(self):
        from storyline import serializers
        sz = serializers.MsgPackStateSerializer
        packed = sz.dumps(self.state)
        new_state = sz.loads(self.plot, packed)
        ensure(new_state).equals(self.state)
