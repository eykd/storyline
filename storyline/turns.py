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
            self.state = states.PlotStateManager(plot, state_dict)
            self.state.clear_messages()
        else:
            self.state = states.PlotState(plot)
            self.state.push(plot.get_start_situation())

    def trigger(self, action, **kwargs):
        self.state.trigger(action, **kwargs)

    def present_story_so_far(self):
        if not self.state.messages:
            self.state.render_situation()

        story_text = u'\n\n'.join(m for m in self.state.messages
                                  if m is not None and m.strip())

        logger.debug("#### The Story:\n%s", story_text)
        md_extensions = self.plot.config['markdown']['extensions']
        story_text = markdown.markdown(story_text, extensions=md_extensions)
        story = typogrify(story_text)

        return story

    def take_turn(self, action=None, **action_kwargs):
        if action is not None:
            self.trigger(action, **action_kwargs)

        story = self.present_story_so_far()
        self.state.clear_messages()

        return story, self.state
