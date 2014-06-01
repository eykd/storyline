# -*- coding: utf-8 -*-
"""storyline.storyfile -- reader for the special storyfile format.
"""
import logging
logger = logging.getLogger('storyline.storyfile')

from path import path
from configobj import ConfigObj

from . import defaults
from . parser import StoryParser, ParserState


def load_plot_from_path(story_path):
    """Load all the series definitions in the given path.
    """
    parser = StoryParser()
    state = ParserState()

    p = path(story_path).expand().abspath()
    for fp in p.walkfiles('*.md'):
        logger.info("Loading {}".format(fp))
        name = unicode(fp.relpath(p).splitext()[0])
        parser.parse(state, name, fp.text())

    CONFIG = p / 'config.ini'
    config = defaults.load_config(CONFIG)
    plot = state.compile(config)

    return plot
