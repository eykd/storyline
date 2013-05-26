# -*- coding: utf-8 -*-
"""storyfile_steps -- steps for testing the storyfile feature.
"""
from behave import given, when, then
from path import path


@given(u'a small navigation story')
def specify_story_file_step(context):
    pass


@when(u'we read the file')
def read_story_file_step(context):
    from storyline import storyfile
    parser = storyfile.StoryParser()
    context.series = parser.parse('navigation', context.text)


@then(u'we get a Series object as a result')
def check_series_obj_step(context):
    from storyline.states import Series
    assert isinstance(context.series, Series)


@then(u'the Series has {num:d} situations')
def check_num_situations_on_series_step(context, num):
    assert len(context.series.ordered) == num


@then(u'we can access the {name} Situation by name')
def check_access_by_name_step(context, name):
    from storyline.states import Situation
    assert isinstance(context.series.by_name[name], Situation)


@then(u'the {situation} Situation has the content "{content}"')
def check_situation_context_step(context, situation, content):
    situation = context.series.by_name[situation]
    assert situation.content.strip() == content.strip(), situation.content.strip()


@then(u'the {situation} Situation has an {directive} directive of "{content}"')
def check_directive_content_step(context, situation, directive, content):
    directive = context.series.by_name[situation].directives[directive]
    assert directive.content.strip() == content.strip(), directive.content.strip()
