# -*- coding: utf-8 -*-
"""storyline.defaults -- default configspec
"""
from path import path
from configobj import ConfigObj
import validate

CONFIG_SPEC = ConfigObj("""
start = string(default="start")

[markdown]
extensions = string_list(default=list())

[states]
base = string_list(default=list())
extensions = string_list(default=list())
""".splitlines(), list_values=False)


def load_config(config=None):
    validator = validate.Validator()
    base = ConfigObj(configspec=CONFIG_SPEC)
    base.validate(validator)
    if config is not None:
        base.merge(ConfigObj(config, configspec=CONFIG_SPEC))
        base.validate(validator)
    return base
