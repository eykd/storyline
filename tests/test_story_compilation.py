# -*- coding: utf-8 -*-
"""tests for parsers.
"""
import unittest
import textwrap

from mock import Mock
from ensure import ensure


class StoryParserTests(unittest.TestCase):
    def setUp(self):
        self.story_text = textwrap.dedent("""\
            This series describes the layout of a small village.

            # = public_house

            The inn where visitors to the village stay. All the men congregate in the hall in the evenings, after the day's labors are done.


            # = main_street

            The main street of the village. Shops and a blacksmith. Horses and carts.


            # = side_street

            ## % This is a comment.

            A side street. Many tradesmen operate their businesses off this street. Shingles hang above each door.

            ## > on_enter
            ## % This is a directive for when the situation is entered.
            foo = 1
            """)

    def test_it_should_parse_and_compile_a_story_definition(self):
        from storyline import parser, entities
        story_parser = parser.StoryParser()
        state = parser.ParserState()

        # When we parse the file and compile it
        story_parser.parse(state, 'navigation', self.story_text)
        # Then we get a Plot object as a result
        # And the Plot has one Series by the name of "navigation"
        plot = state.compile()
        ensure(plot).is_an(entities.Plot)
        ensure(plot.by_name).has_length(1)
        series = plot.by_name['navigation']
        ensure(series).is_an(entities.Series)
        # And the Series has 3 situations
        ensure(series.ordered).has_length(3)
        # And we can access the side_street Situation by name
        situation = series.by_name['side_street']
        ensure(situation).is_an(entities.Situation)
        # And the side_street Situation has the content
        ensure(situation.content).equals("\n\nA side street. Many tradesmen operate their businesses off this street. Shingles hang above each door.\n")
        # And the side_street Situation has an on_enter directive of "foo = 1"
        ensure(situation.directives).contains('on_enter')
        directive = situation.directives['on_enter']
        ensure(directive).is_an(entities.Directive)
        ensure(directive.content).equals("foo = 1")
