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
                name='start', series='foo', content="Hello, start!",
                directives={
                    'on_enter': entities.Directive(name='on_exit', situation='start', content="Enter start!"),
                    'on_exit': entities.Directive(name='on_exit', situation='start', content="Exit start!"),
                }
            ),
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
        ensure(self.turn_mgr.state.stack).equals([('foo', 'bar')])

    def test_it_should_create_fresh_plotstate_when_no_state_dict_is_provided(self):
        from storyline import states
        from storyline import turns
        turn_mgr = turns.TurnManager(self.plot)
        ensure(turn_mgr.state).is_a(states.PlotState)
        ensure(sorted(turn_mgr.state.keys())).equals(sorted(self.turn_mgr.state.keys()))
        ensure(turn_mgr.state.stack).equals([('foo', 'start')])

    def test_it_should_trigger_a_directive(self):
        mock_state = Mock()
        new_state = Mock()
        mock_state.trigger.return_value = new_state
        self.turn_mgr.state = mock_state
        self.turn_mgr.trigger('do_something')
        ensure(mock_state.trigger.call_count).equals(1)
        ensure(mock_state.trigger.call_args).equals(call('do_something'))
        ensure(self.turn_mgr.state).is_(new_state)

    def test_it_should_present_the_story_so_far_by_showing_messages(self):
        self.turn_mgr.trigger('do_something')
        story = self.turn_mgr.present_story_so_far()
        ensure(story).equals('<p>Don&#8217;t just stand&nbsp;there!</p>')

    def test_it_should_present_the_story_so_far_by_showing_the_current_situation_when_there_are_no_messages(self):
        story = self.turn_mgr.present_story_so_far()
        ensure(story).equals('<p>Hello,&nbsp;bar!</p>')

    def test_it_should_take_a_turn_by_performing_an_action(self):
        story, state = self.turn_mgr.take_turn('do_something')
        ensure(story).equals('<p>Don&#8217;t just stand&nbsp;there!</p>')
        ensure(state).is_(self.turn_mgr.state)
        ensure(self.turn_mgr.state.messages).is_empty()

    def test_it_should_take_a_turn_with_no_action_and_show_the_current_situation(self):
        story, state = self.turn_mgr.take_turn()
        ensure(story).equals('<p>Hello,&nbsp;bar!</p>')
        ensure(state).is_(self.turn_mgr.state)
        ensure(self.turn_mgr.state.messages).is_empty()
