# -*- coding: utf-8 -*-
"""plot_steps -- step definitions for setting up plots.
"""
from behave import given, when, then


@given(u'a Series definition')
def define_series_data_step(context):
    context.series_def = {
    }


@when(u'I instantiate a Plot with a Series definition')
def instantiate_plot_step(context):
    from storyline.states import Plot
    context.plot = Plot(context.series_def)


@then(u'I have a Plot')
def check_plot_step(context):
    assert context.plot
