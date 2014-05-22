# -*- coding: utf-8 -*-
"""tests for parsers.
"""
import unittest
import textwrap

from mock import Mock
from ensure import ensure


class StoryParserTests(unittest.TestCase):
    def setUp(self):
        from storyline import parser
        self.parser = parser.StoryParser()

    def test_on_comment_should_be_no_op(self):
        state = None  # Ensure that any method calls raise exceptions. :)
        ensure(self.parser.parse_line).called_with(state, '# % Some comment...').is_none()

    def test_on_directive_should_add_directive_by_name(self):
        state = Mock()
        self.parser.parse_line(state, "## > on_enter")
        state.add_directive.assert_called_with('on_enter')

    def test_on_new_section_should_add_situation_by_name(self):
        state = Mock()
        self.parser.parse_line(state, "# = intro")
        state.add_situation.assert_called_with('intro')

    def test_on_line_should_add_line(self):
        state = Mock()
        self.parser.parse_line(state, "Hello world.")
        state.add_line.assert_called_with('Hello world.')

    def test_parse_should_parse_and_add_the_series(self):
        state = Mock()
        storydef = textwrap.dedent("""\
            # = intro 1
            1
            2 Hurrying through the rainswept November night, you're glad to see the bright
            3 lights of the Opera House. It's surprising that there aren't more people about
            4 but, hey, what do you expect in a cheap demo game...?
            5
            6 [Onward!](replace!rooms::foyer)
            7
            ## > on_enter 1
            8 {{ I.am("wearing cloak", True) }}
            9 {{ flags.add("items::Opera Cloak") }}""")
        self.parser.parse(state, 'foo', storydef)
        ensure(state.add_series.call_count).equals(1)
        ensure(state.add_situation.call_count).equals(1)
        ensure(state.add_directive.call_count).equals(1)
        ensure(state.add_line.call_count).equals(9)
