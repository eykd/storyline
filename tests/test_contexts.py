# -*- coding: utf-8 -*-
"""tests for storyline.contexts
"""
import unittest

from ensure import ensure


class ContextMixinTests(unittest.TestCase):
    def test_it_should_wrap_methods_returning_None_with_empty_string_as_return_value(self):
        from storyline import contexts

        class ContextDict(contexts.ContextMixin, dict):
            pass

        d = ContextDict()
        ensure(d.clear()).equals('')


class ContextStateTests(unittest.TestCase):
    def test_it_should_set_items(self):
        from storyline import contexts

        c = contexts.ContextState()
        result = c.set('foo', 'bar')
        ensure(c).contains('foo')
        ensure(c['foo']).equals('bar')
        ensure(result).equals('')

    def test_it_should_check_values(self):
        from storyline import contexts

        c = contexts.ContextState()
        c.set('foo', 'bar')
        for name in ('is_', 'am', 'are'):
            ensure(getattr(c, name)).called_with('foo', 'bar').is_true()
            ensure(getattr(c, name)).called_with('foo', 'baz').is_false()
            ensure(getattr(c, name)).called_with('foo').equals('bar')
            ensure(getattr(c, name)).called_with('blah').equals('')

    def test_it_should_increment_values(self):
        from storyline import contexts

        c = contexts.ContextState(foo=5)
        ensure(c.incr('foo')).equals('')
        ensure(c['foo']).equals(6)
        c.incr('foo', 4)
        ensure(c['foo']).equals(10)

        c.incr('bar')
        ensure(c['bar']).equals(1)

        c.incr('baz', 10)
        ensure(c['baz']).equals(10)

    def test_it_should_raise_typeerror_when_incrementing_nonnumeric_values(self):
        from storyline import contexts

        c = contexts.ContextState(foo='bar')
        ensure(c.incr).called_with('foo').raises(TypeError)

    def test_it_should_decrement_values(self):
        from storyline import contexts

        c = contexts.ContextState(foo=5)
        ensure(c.decr('foo')).equals('')
        ensure(c['foo']).equals(4)
        c.decr('foo', 4)
        ensure(c['foo']).equals(0)

        c.decr('bar')
        ensure(c['bar']).equals(-1)

        c.decr('baz', 10)
        ensure(c['baz']).equals(-10)

    def test_it_should_raise_typeerror_when_decrementing_nonnumeric_values(self):
        from storyline import contexts

        c = contexts.ContextState(foo='bar')
        ensure(c.decr).called_with('foo').raises(TypeError)
