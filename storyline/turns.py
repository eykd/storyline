# -*- coding: utf-8 -*-
"""storyline.turns -- turn-taking for story plots
"""
import logging
logger = logging.getLogger('turns')

import markdown
from typogrify.filters import typogrify

from . import states


class TurnManager(object):
    def __init__(self, plot, state_dict=None):
        self.plot = plot

        if state_dict is not None:
            state = states.PlotState(plot, state_dict)
            state = state.clear_messages()
        else:
            state = states.PlotState(plot)

        self.state = state

    def trigger(self, action, **kwargs):
        self.state = self.state.trigger(action, **kwargs)

    def present_story_so_far(self):
        if self.state.messages:
            story_text = u'\n\n'.join(m for m in self.state.messages
                                      if m is not None and m.strip())
        else:
            story_text = self.state.current(self.plot).content

        logger.debug("#### The Story:\n%s", story_text)
        md_extensions = self.plot.config['markdown']['extensions']
        story_text = markdown.markdown(story_text, extensions=md_extensions)
        story = typogrify(story_text)

        return story

    def take_turn(self, action=None, **action_kwargs):
        if action is not None:
            self.trigger(action, **action_kwargs)

        story = self.present_story_so_far()
        state = self.state.to_dict()

        self.state.clear_messages()
        return story, state
