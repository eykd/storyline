# -*- coding: utf-8 -*-
"""storyline.context
"""
import inspect


class ContextMixin(object):
    """Mixin for data structures used within template contexts.

    Wraps methods on the object to return the empty string instead of None.
    """
    def __getattribute__(self, name):
        """Coerce methods that return None to return the empty string.
        """
        value = object.__getattribute__(self, name)
        if inspect.isbuiltin(value) and hasattr(value, '__call__'):
            meth = value

            def wrapper(*args, **kwargs):
                result = meth(*args, **kwargs)
                if result is None:
                    return u''
                else:
                    return result
            return wrapper
        else:
            return value


class ContextState(ContextMixin, dict):
    """A context-ready dict with superpowers.
    """
    def set(self, key, value):
        self[key] = value
        return u''

    def is_(self, key, value=None):
        if value is None:
            return self.get(key)
        else:
            return self.get(key) == value

    are = is_
    am = is_

    def incr(self, key, value=1):
        """Increment a numeric value.
        """
        try:
            self[key] += value
        except TypeError:
            raise TypeError('Tried to increment non-numeric key {!r} ({!r}) by {}'.format(
                key, self[key], value
            ))
        except KeyError:
            self[key] = value

        return u''

    def decr(self, key, value=1):
        """Decrement a numeric value.
        """
        try:
            self[key] -= value
        except TypeError:
            raise TypeError('Tried to decrement non-numeric key {!r} ({!r}) by {}'.format(
                key, self[key], value
            ))
        except KeyError:
            self[key] = -value

        return u''


class ContextSet(ContextMixin, set):
    """A context-ready set.
    """
    pass


class ContextList(ContextMixin, list):
    """A context-ready list.
    """
    pass
