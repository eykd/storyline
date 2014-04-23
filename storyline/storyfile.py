# -*- coding: utf-8 -*-
"""storyline.storyfile -- reader for the special storyfile format.
"""
import re
import warnings
import logging
logger = logging.getLogger('storyline')

from path import path
from configobj import ConfigObj

from . import defaults
from .states import Series, Situation, Directive

_spaces_cp = re.compile(' +')
_slugsub_cp = re.compile(r'\W')


def slugify(name):
    return _slugsub_cp.sub('', name).replace('-', '_')


class StoryParser(object):
    event_map = {
        '# =': 'new_section',
        '# %': 'comment',
        '## %': 'comment',
        '## >': 'directive',
    }

    def parse(self, name, storydef):
        state = ParserState(name)
        for line in storydef.splitlines():
            for key in self.event_map:
                if line.startswith(key):
                    handler = getattr(self, 'on_' + self.event_map[key])
                    handler(state, line)
                    break
            else:
                self.on_line(state, line)

        while state.mode:
            result = state.close()

        return result

    def on_line(self, state, line):
        state.add_line(line)

    def on_new_section(self, state, line):
        name = line.split('=', 1)[1].strip()
        state.add_situation(name)

    def on_directive(self, state, line):
        name = line.split('>', 1)[1].strip()
        state.add_directive(name)

    def on_comment(self, state, line):
        # No-op: just a source comment.
        pass


class ParserState(object):
    def __init__(self, name):
        self.series = Series(name)
        self.situation = None
        self.directive = None
        self.buffer = []
        self.mode = ['series']

    def add_line(self, line):
        self.buffer.append(line.rstrip())

    def get_buffer(self):
        content = u'\n'.join(self.buffer).rstrip()
        self.buffer[:] = ()
        return content

    def close(self):
        self.finish()
        mode = self.mode.pop()
        result = getattr(self, mode)
        setattr(self, mode, None)
        close_method = 'close_' + mode
        if hasattr(self, close_method):
            getattr(self, close_method)()
        return result

    def finish(self):
        mode = self.mode[-1]
        obj = getattr(self, mode)
        if obj is not None:
            content = self.get_buffer()
            if content.strip():
                if obj.content.strip():
                    obj.content += u'\n' + content
                else:
                    obj.content = content
            finish_method = 'finish_' + mode
            if hasattr(self, finish_method):
                getattr(self, finish_method)()

    def add_situation(self, name):
        while self.mode[-1] != 'series':
            self.close()
        self.finish()
        self.series.content = self.get_buffer()
        self.mode.append('situation')
        self.situation = s = Situation(name)
        self.series.add_situation(s)

    def add_directive(self, name):
        while self.mode[-1] not in ('series', 'situation'):
            self.close()
        self.finish()

        if self.situation is None:
            warnings.warn("Encountered a directive (`## > %s`) outside the context of a situation. It will be ignored." % name)
            return

        self.mode.append('directive')
        d = Directive(name)
        self.directive = d
        self.situation.add_directive(d)


def load_path(story_path, plot):
    """Load all the series definitions in the given path.
    """
    parser = StoryParser()

    p = path(story_path).expand().abspath()
    for fp in p.walkfiles('*.story'):
        logger.info("Loading {}".format(fp))
        name = unicode(fp.relpath(p).splitext()[0])
        plot.add_series(parser.parse(name, fp.text()))

    CONFIG = p / 'config.ini'
    if CONFIG.exists():
        plot.config.merge(ConfigObj(CONFIG, configspec=defaults.CONFIG_SPEC))
