# -*- coding: utf-8 -*-
"""tests for storyline.states.PlotState
"""
import unittest

from ensure import ensure

from nonobvious import frozenlist, frozenset, frozendict


class PlotStateTests(unittest.TestCase):
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
        self.state = states.PlotState(
            self.plot,
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

    def test_plot_state_can_be_instantiated(self):
        ensure(self.state.stack).is_a(frozenlist)
        ensure(self.state.situation).is_a(tuple)
        ensure(self.state.messages).is_a(frozenlist)
        ensure(self.state.flags).is_a(frozenset)
        ensure(self.state.this).is_a(frozendict)
        ensure(self.state.locations).is_a(frozendict)
        for value in self.state.locations.itervalues():
            ensure(value).is_a(frozendict)

    def test_it_should_return_the_top_state(self):
        ensure(self.state.top).equals(('foo', 'bar'))

    def test_it_should_copy_itself_with_the_plot(self):
        a_copy = self.state.copy()
        ensure(a_copy.plot).is_(self.state.plot)

    def test_it_should_create_a_context(self):
        from storyline import contexts
        ctx = self.state.as_context()

        for synonym in 'this its I my we our he his she'.split():
            value = ctx[synonym]
            ensure(value).equals(self.state.this)
            ensure(value).is_a(contexts.ContextState)

        ensure(ctx['here']).equals(self.state.locations['foo::bar'])
        ensure(ctx['here']).is_a(contexts.ContextState)

        ensure(ctx['elsewhere']).equals(self.state.locations)
        for value in ctx['elsewhere'].itervalues():
            ensure(value).is_a(contexts.ContextState)

        ensure(ctx['flags']).equals(self.state.flags)
        ensure(ctx['flags']).is_a(contexts.ContextSet)

        ensure(ctx['commands']).is_a(contexts.ContextList)
        ensure(ctx['commands']).is_empty()

        ftype = type(lambda: None)
        for command in 'push pop replace select reset'.split():
            ensure(ctx[command]).is_a(ftype)

    def test_its_context_should_have_push_command(self):
        ctx = self.state.as_context()
        ctx['push']('foo')
        ensure(ctx['commands']).has_length(1)
        ensure(ctx['commands']).contains(('push', 'foo'))

    def test_its_context_should_have_pop_command(self):
        ctx = self.state.as_context()
        ctx['pop']()
        ensure(ctx['commands']).has_length(1)
        ensure(ctx['commands']).contains(('pop',))

    def test_its_context_should_have_replace_command(self):
        ctx = self.state.as_context()
        ctx['replace']('foo')
        ensure(ctx['commands']).has_length(1)
        ensure(ctx['commands']).contains(('replace', 'foo'))

    def test_its_context_should_have_select_command(self):
        ctx = self.state.as_context()
        ctx['select']('foo')
        ensure(ctx['commands']).has_length(1)
        ensure(ctx['commands']).contains(('replace', 'foo'))

    def test_its_context_should_have_reset_command(self):
        ctx = self.state.as_context()
        ctx['reset']('foo')
        ensure(ctx['commands']).has_length(1)
        ensure(ctx['commands']).contains(('reset', 'foo'))

        ctx['reset']()
        ensure(ctx['commands']).has_length(2)
        ensure(ctx['commands']).contains(('reset', None))

    def test_it_should_accept_a_context_and_produce_a_new_state(self):
        ctx = self.state.as_context()
        ctx['this'].set('INT', 1)
        new_state = self.state.from_context(ctx)
        ensure(new_state).is_not(self.state)
        ensure(new_state.copy(this=self.state.this)).equals(self.state)
        ensure(new_state.this['INT']).equals(1)

    def test_it_should_accept_a_context_with_commands_and_produce_a_new_state(self):
        ctx = self.state.as_context()
        ctx['this'].set('INT', 1)
        ctx['push']('foo::baz')
        new_state = self.state.from_context(ctx)
        ensure(new_state).is_not(self.state)
        ensure(new_state.stack).has_length(2)
        ensure(new_state.stack).equals([('foo', 'bar'), ('foo', 'baz')])
        ensure(new_state.messages).equals(['Exit bar!', 'Enter baz!', 'Hello, baz!'])
        ensure(new_state.this['INT']).equals(1)

    def test_it_should_clear_messages(self):
        new_state = self.state.copy(messages=['foo', 'bar'])
        newer_state = new_state.clear_messages()
        ensure(newer_state).is_not(new_state)
        ensure(newer_state.messages).is_empty()

    def test_it_should_add_a_message(self):
        new_state = self.state.add_message('foo')
        ensure(new_state).is_not(self.state)
        ensure(new_state.messages).contains('foo')

    def test_it_should_not_add_an_empty_message(self):
        new_state = self.state.add_message('')
        ensure(new_state).is_(self.state)
        ensure(new_state.messages).is_empty()

    def test_it_should_return_the_current_situation(self):
        series, situation = self.state.situation
        ensure(self.state.current()).is_(self.state.plot.by_name[series].by_name[situation])

    def test_it_should_trigger_a_directive(self):
        new_state = self.state.trigger('on_enter')
        ensure(new_state.messages).contains('Enter bar!')

    def test_it_should_exit_the_current_situation_and_set_to_None(self):
        new_state = self.state._exit()
        ensure(new_state.situation).is_none()
        ensure(new_state.messages).contains('Exit bar!')

    def test_it_should_enter_a_new_situation(self):
        new_state = self.state._enter('foo::baz')
        ensure(new_state.situation).does_not_equal(self.state.situation)
        ensure(new_state.situation).equals(('foo', 'baz'))
        ensure(new_state.messages).contains('Enter bar!')

    def test_it_should_push_a_situation(self):
        new_state = self.state.push('foo::baz')
        ensure(new_state).is_not(self.state)
        ensure(new_state.stack).has_length(2)
        ensure(new_state.stack).equals([('foo', 'bar'), ('foo', 'baz')])
        ensure(new_state.messages).equals(['Exit bar!', 'Enter baz!', 'Hello, baz!'])

    def test_it_should_pop_a_situation(self):
        new_state = self.state.push('foo::baz').pop()
        ensure(new_state).is_not(self.state)
        ensure(new_state.stack).has_length(1)
        ensure(new_state.stack).equals([('foo', 'bar')])
        ensure(new_state.messages).equals(
            ['Exit bar!', 'Enter baz!', 'Hello, baz!', 'Exit baz!', 'Enter bar!', 'Hello, bar!'])

    def test_it_should_pop_the_last_situation_and_restart(self):
        new_state = self.state.pop()
        ensure(new_state).is_not(self.state)
        ensure(new_state.stack).has_length(1)
        ensure(new_state.stack).equals([('foo', 'start')])
        ensure(new_state.messages).equals(
            ['Exit bar!', 'Enter start!', 'Hello, start!'])

    def test_it_should_replace_the_situation(self):
        new_state = self.state.replace('foo::baz')
        ensure(new_state).is_not(self.state)
        ensure(new_state.stack).has_length(1)
        ensure(new_state.stack).equals([('foo', 'baz')])
        ensure(new_state.messages).equals(['Exit bar!', 'Enter baz!', 'Hello, baz!'])

    def test_it_should_reset_the_situation_to_start(self):
        new_state = self.state.reset()
        ensure(new_state).is_not(self.state)
        ensure(new_state.stack).has_length(1)
        ensure(new_state.stack).equals([('foo', 'start')])
        ensure(new_state.situation).equals(('foo', 'start'))
        ensure(new_state.messages).equals(['Exit bar!', 'Enter start!', 'Hello, start!'])
        ensure(new_state.flags).is_empty()
        ensure(new_state.this).is_empty()
        ensure(new_state.locations).is_empty()
