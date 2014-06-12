# -*- coding: utf-8 -*-
"""tests for storyline.states.stack
"""
import unittest

from ensure import ensure

from nonobvious import frozenlist, frozenset, frozendict

import helpers


class StackStateTests(helpers.StateTests):
    def setUp(self):
        super(StackStateTests, self).setUp()

        from storyline.states.stack import StackState
        self.messages = []
        self.state = StackState(
            self.plot,
            self.messages,
            stack=[('foo', 'bar')],
            situation=('foo', 'bar'),
        )

    def test_plot_state_can_be_instantiated(self):
        ensure(self.state.stack).is_a(frozenlist)
        ensure(self.state.situation).is_a(tuple)
        ensure(self.state.messages).is_(self.messages)

    def test_it_should_return_the_top_state(self):
        ensure(self.state.top).equals(('foo', 'bar'))

    def test_it_should_copy_itself_with_the_plot(self):
        a_copy = self.state.copy()
        ensure(a_copy.plot).is_(self.state.plot)
        ensure(a_copy.messages).is_(self.messages)

    def test_it_should_create_a_context(self):
        commands = []
        ctx = self.state.as_context(commands)

        ftype = type(lambda: None)
        for command in 'push pop replace select reset'.split():
            ensure(ctx[command]).is_a(ftype)

    def test_its_context_should_have_push_command(self):
        commands = []
        ctx = self.state.as_context(commands)
        ctx['push']('foo')
        ensure(commands).has_length(1)
        ensure(commands).contains(('push', 'foo'))

    def test_its_context_should_have_pop_command(self):
        commands = []
        ctx = self.state.as_context(commands)
        ctx['pop']()
        ensure(commands).has_length(1)
        ensure(commands).contains(('pop',))

    def test_its_context_should_have_replace_command(self):
        commands = []
        ctx = self.state.as_context(commands)
        ctx['replace']('foo')
        ensure(commands).has_length(1)
        ensure(commands).contains(('replace', 'foo'))

    def test_its_context_should_have_select_command(self):
        commands = []
        ctx = self.state.as_context(commands)
        ctx['select']('foo')
        ensure(commands).has_length(1)
        ensure(commands).contains(('replace', 'foo'))

    def test_its_context_should_have_reset_command(self):
        commands = []
        ctx = self.state.as_context(commands)
        ctx['reset']('foo')
        ensure(commands).has_length(1)
        ensure(commands).contains(('reset', 'foo'))

        ctx['reset']()
        ensure(commands).has_length(2)
        ensure(commands).contains(('reset', None))

    def test_it_should_accept_a_context_and_produce_a_new_state(self):
        commands = []
        ctx = self.state.as_context(commands)
        new_state = self.state.from_context(ctx)
        ensure(new_state).is_(self.state)

    def test_it_should_accept_a_context_with_commands_and_produce_a_new_state(self):
        commands = []
        ctx = self.state.as_context(commands)
        ctx['push']('foo::baz')
        new_state = self.state.from_context(ctx)
        ensure(new_state).is_(self.state)

    def test_it_should_add_a_message(self):
        self.state.add_message('foo')
        ensure(self.ex_messages(self.messages)).contains('foo')

    def test_it_should_not_add_an_empty_message(self):
        new_state = self.state.add_message('')
        ensure(new_state).is_(self.state)
        ensure(new_state.messages).is_empty()

    def test_it_should_return_the_current_situation(self):
        series, situation = self.state.situation
        ensure(self.state._current()).is_(self.state.plot.by_name[series].by_name[situation])

    def test_it_should_get_a_directives_content_for_an_event(self):
        import jinja2
        result = self.state.get_event('on_enter')
        ensure(result).is_a(jinja2.Template)
        ensure(self.ex_template(result)).equals('Enter bar!')

    def test_it_should_exit_the_current_situation_and_set_to_None(self):
        new_state = self.state._exit()
        ensure(new_state.situation).is_none()
        ensure(self.ex_messages(new_state.messages)).contains('Exit bar!')

    def test_it_should_enter_a_new_situation(self):
        new_state = self.state._enter('foo::baz')
        ensure(new_state.situation).does_not_equal(self.state.situation)
        ensure(new_state.situation).equals(('foo', 'baz'))
        ensure(self.ex_messages(new_state.messages)).contains('Enter bar!')

    def test_it_should_push_a_situation(self):
        new_state = self.state.push('foo::baz')
        ensure(new_state).is_not(self.state)
        ensure(new_state.stack).has_length(2)
        ensure(new_state.stack).equals([('foo', 'bar'), ('foo', 'baz')])
        ensure(self.ex_messages(new_state.messages)).equals(['Exit bar!', 'Enter baz!', 'Hello, baz!'])

    def test_it_should_pop_a_situation(self):
        new_state = self.state.push('foo::baz').pop()
        ensure(new_state).is_not(self.state)
        ensure(new_state.stack).has_length(1)
        ensure(new_state.stack).equals([('foo', 'bar')])
        ensure(self.ex_messages(new_state.messages)).equals(
            ['Exit bar!', 'Enter baz!', 'Hello, baz!', 'Exit baz!', 'Enter bar!', 'Hello, bar!'])

    def test_it_should_pop_the_last_situation_and_restart(self):
        new_state = self.state.pop()
        ensure(new_state).is_not(self.state)
        ensure(new_state.stack).has_length(1)
        ensure(new_state.stack).equals([('foo', 'start')])
        ensure(self.ex_messages(new_state.messages)).equals(
            ['Exit bar!', 'Enter start!', 'Hello, start!'])

    def test_it_should_replace_the_situation(self):
        new_state = self.state.replace('foo::baz')
        ensure(new_state).is_not(self.state)
        ensure(new_state.stack).has_length(1)
        ensure(new_state.stack).equals([('foo', 'baz')])
        ensure(self.ex_messages(new_state.messages)).equals(['Exit bar!', 'Enter baz!', 'Hello, baz!'])

    def test_it_should_reset_the_situation_to_start(self):
        new_state = self.state.reset()
        ensure(new_state).is_not(self.state)
        ensure(new_state.stack).is_empty()
        ensure(new_state.situation).is_none()
        ensure(self.ex_messages(new_state.messages)).equals(['Exit bar!'])
