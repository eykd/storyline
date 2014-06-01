# -*- coding: utf-8 -*-
"""cloak_steps -- Cloak of Darkness feature spec steps.
"""
from behave import given, when, then
from path import path

from ensure import ensure

PATH = path(__file__).abspath().dirname()

CLOAK_PATH = PATH / 'data' / 'cloak'


@given(u'a Plot definition for the Cloak of Darkness spec')
def plot_definition_step(context):
    CLOAK_PATH.exists()


@when(u'I read the Cloak of Darkness series definitions')
def read_series_definitions_step(context):
    from storyline import storyfile
    context.plot = storyfile.load_plot_from_path(CLOAK_PATH)


@then(u'I have a Plot with the Cloak of Darkness Series definitions')
def check_plot_series_step(context):
    plot = context.plot
    for name in ('rooms', 'items', 'actions', 'start'):
        ensure(plot.by_name).contains(name)


@then(u'I can start a new Plot State')
def start_plot_state_step(context):
    from storyline import states
    state = context.state = states.PlotState(context.plot).push(context.plot.get_start_situation())
    context.situation = state.current()


@given(u'I am in the "{situation}" situation of "{series}"')
@then(u'I am in the "{situation}" situation of "{series}"')
def check_situation_step(context, situation, series):
    state = context.state
    ensure(state.stack[-1]).equals((series, situation))
    ensure(state.situation).equals((series, situation))


@then(u'the "{flag_name}" flag should be "{state}"')
@then(u'the "{flag_name}" flag should be "{state}" ({datatype})')
def check_flag_state_step(context, flag_name, state, datatype="unicode"):
    if datatype == 'bool':
        state = state.lower()
        if state == 'true':
            state = True
        elif state == 'false':
            state = False
        state = bool(state)
    else:
        state = getattr(__builtins__, datatype)(state)
    ensure(context.state.this.get(flag_name, None)).equals(state)


@given(u'the stack has a length of {length:d}')
@then(u'the stack has a length of {length:d}')
def check_stack_length_step(context, length):
    ensure(len(context.state.stack)).equals(length)


@when(u'I choose "{action}"')
def choose_action_step(context, action):
    state = context.state
    state = context.state = state.trigger(action)
    context.situation = state.current()


@then(u'the last message says "{message}"')
def check_last_message_step(context, message):
    message = message.replace(u'\\n', u'\n')
    state = context.state
    last_index = -1
    last_message = state.messages[last_index]
    while last_message is not None and not last_message.strip():
        last_index -= 1
        last_message = state.messages[last_index]
    ensure(last_message).equals(message)
