# -*- coding: utf-8 -*-
"""pavement.py -- paver tasks for storyline.
"""
from paver.easy import task, sh, consume_args


@task
@consume_args
def start(args):
    if not args:
        args = ("--debug", "features/steps/data/cloak/")
    sh('./bin/storyline start %s' % ' '.join(args))
