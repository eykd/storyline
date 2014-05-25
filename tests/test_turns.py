# -*- coding: utf-8 -*-
"""tests for storyline.turns
"""
import unittest

from mock import Mock, call
from ensure import ensure


class TurnManagerTests(unittest.TestCase):
    def setUp(self):
        from storyline import entities
        situations = [
            entities.Situation(
                name='bar', series='foo', content="Hello, bar!",
                directives={
                    'do_something': entities.Directive(name='do_something', situation='bar', content="Don't just stand there!"),
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

        self.state_dict = dict(
            stack=[('foo', 'bar')],
            situation=('foo', 'bar'),
            messages=[],
            flags=('blah', 'la'),
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

        from storyline import turns
        self.turn_mgr = turns.TurnManager(self.plot, self.state_dict)

    def test_it_should_create_plotstate_from_state_dict(self):
        from storyline import states
        ensure(self.turn_mgr.state).is_a(states.PlotState)
        ensure(sorted(self.turn_mgr.state.keys())).equals(sorted(self.state_dict.keys()))

    def test_it_should_create_fresh_plotstate_when_no_state_dict_is_provided(self):
        from storyline import states
        from storyline import turns
        turn_mgr = turns.TurnManager(self.plot)
        ensure(turn_mgr.state).is_a(states.PlotState)
        ensure(sorted(turn_mgr.state.keys())).equals(sorted(self.turn_mgr.state.keys()))

    def test_it_should_trigger_a_directive(self):
        mock_state = Mock()
        new_state = Mock()
        mock_state.trigger.return_value = new_state
        self.turn_mgr.state = mock_state
        self.turn_mgr.trigger('do_something')
        ensure(mock_state.trigger.call_count).equals(1)
        ensure(mock_state.trigger.call_args).equals(call('do_something'))
        ensure(self.turn_mgr.state).is_(new_state)
