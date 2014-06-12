# -*- coding: utf-8 -*-
"""storyline.plugins

A simple plugin framework.

Based on the design at http://martyalchin.com/2008/jan/10/simple-plugin-framework/
"""
import importlib


def import_plugin(dotted_path):
    """Given a dotted path (`module.ClassName`), import and return the class.
    """
    module_name, class_name = dotted_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    try:
        return getattr(module, class_name)
    except AttributeError:
        raise ImportError("No such class {} in {}".format(class_name, module_name))


class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)
