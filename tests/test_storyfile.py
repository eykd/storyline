# -*- coding: utf-8 -*-
"""test_storyfile -- tests for the storyfile loader.
"""
import unittest


SAMPLE_STORYFILE = """
This series describes the layout of a small village.

# = public_house

The inn where visitors to the village stay. All the men congregate in the hall in the evenings, after the day's labors are done.


# = main_street

The main street of the village. Shops and a blacksmith. Horses and carts.


# = side_street

## ! This is a comment.

A side street. Many tradesmen operate their businesses off this street. Shingles hang above each door.

## > on_enter
## ! This is a directive for when the situation is entered.
foo = 1
"""


class StoryFileParserStateTests(unittest.TestCase):
    def setUp(self):
        from storyline import storyfile
        self.sf = storyfile

    def test_parse_the_file(self):
        parser = self.parser = self.sf.StoryParser()
        self.series = parser.parse('village', SAMPLE_STORYFILE)
