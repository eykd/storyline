# -*- coding: utf-8 -*-
"""pavement.py -- paver tasks for storyline.
"""
from paver.easy import task, sh, consume_args


@task
@consume_args
def start(args):
    sh('./bin/storyline start --debug features/steps/data/cloak/')
