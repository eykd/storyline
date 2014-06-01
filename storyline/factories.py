# -*- coding: utf-8 -*-
"""storyline.factories

Factories for generating story objects.
"""
import re
import urllib
import warnings

from . import entities
from . import defaults
from nonobvious import frozendict, frozenlist


class Factory(object):
    kind = 'factory'

    def __init__(self, name):
        self.name = name
        self.lines = []

    def add_line(self, line):
        self.lines.append(line.rstrip())


class PlotFactory(object):
    kind = 'plot'

    def __init__(self):
        self.series = []
        self.config = defaults.load_config()

    def add_series(self, name):
        factory = SeriesFactory(name)
        self.series.append(factory)
        return factory

    def add_config(self, config):
        self.config.merge(defaults.load_config(config))

    def build(self):
        return entities.Plot(
            by_name = frozendict((s.name, s.build()) for s in self.series),
            config = self.config,
        )


class SeriesFactory(Factory):
    kind = 'series'

    def __init__(self, name):
        super(SeriesFactory, self).__init__(name)
        self.situations = []

    def add_situation(self, name):
        factory = SituationFactory(name, self.name)
        self.situations.append(factory)
        return factory

    def build(self):
        situations = frozenlist(s.build() for s in self.situations)
        return entities.Series(
            name = self.name,
            content = u"\n".join(self.lines),
            by_name = frozendict((s.name, s) for s in situations),
            ordered = situations,
        )


class SituationFactory(Factory):
    kind = 'situation'

    link_cp = re.compile(r'\[(?P<text>.+?)\]\((?P<target>.+?)\)', re.MULTILINE)

    def __init__(self, name, series_name):
        super(SituationFactory, self).__init__(name)
        self.series_name = series_name
        self.directives = {}

    def add_directive(self, name):
        factory = DirectiveFactory(name, self.name)
        self.directives[name] = factory
        return factory

    def parse_directive(self, anchor_text, target):
        if target not in self.directives:
            # We need to parse an inline directive.
            if target == '!':
                # !: Trigger an event of the same name as anchor text
                if anchor_text not in self.directives:
                    warnings.warn("No directive defined for [{}](!) in {}".format(anchor_text, self.name))
                    d = self.add_directive(anchor_text)
                target = urllib.quote_plus(anchor_text)
            if '!' in target:
                if target.startswith('!'):
                    # !event: Trigger the event named
                    action = 'trigger'
                    obj = target[1:]
                else:
                    # action!arg: Call the action with the given argument
                    action, obj = [i.strip() for i in target.split('!', 1)]

                # Build a little script for the new directive to run.
                script = u'{{{{ {action}({obj}) }}}}'.format(
                    action = action,
                    obj = u'"{}"'.format(obj)
                )
                d = self.add_directive(anchor_text)
                d.add_line(script)
                target = urllib.quote_plus(anchor_text)

        return u'[{anchor_text}]({url})'.format(
            anchor_text = anchor_text,
            url = target,
        )

    def compile_content(self):
        """Identify and parse directives from Markdown links in the content.

        Return the transformed content which properly address the directives in
        the dict.
        """
        content = u"\n".join(self.lines)
        new_content = []
        start = 0
        # Find all links of the form `[anchor text](directive)`:
        for match in self.link_cp.finditer(content):
            new_content.append(content[start:match.start()])
            start = match.end()
            anchor_text, target = match.groups()
            md_link = self.parse_directive(anchor_text, target)
            new_content.append(md_link)

        new_content.append(content[start:])

        return u''.join(new_content)

    def build(self):
        content = self.compile_content()
        return entities.Situation(
            name = self.name,
            series = self.series_name,
            content = content,
            directives = frozendict((name, d.build()) for name, d in self.directives.iteritems()),
        )


class DirectiveFactory(Factory):
    kind = 'directive'

    def __init__(self, name, situation_name):
        super(DirectiveFactory, self).__init__(name)
        self.situation_name = situation_name
        self.directives = []

    def build(self):
        return entities.Directive(
            name = self.name,
            situation = self.situation_name,
            content = u'\n'.join(self.lines),
        )
