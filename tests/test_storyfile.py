# -*- coding: utf-8 -*-
"""tests for storyline.storyfile
"""
import unittest

from path import path
from ensure import ensure


class LoadPlotFromPathTests(unittest.TestCase):
    def test_it_should_load_a_path_and_return_a_plot(self):
        from storyline import storyfile
        PATH = path(__file__).abspath().dirname().parent / 'features' / 'steps' / 'data' / 'cloak'
        plot = storyfile.load_plot_from_path(PATH)
        ensure(plot.by_name).contains('start')
