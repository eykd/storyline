# -*- coding: utf-8 -*-
"""storyline.presenters -- presenters for rendering raw messages into output.
"""


class HTMLPresenter(object):
    def __init__(self, messages):
        self.messages = messages
