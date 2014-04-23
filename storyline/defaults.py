# -*- coding: utf-8 -*-
"""storyline.defaults -- default configspec
"""
from configobj import ConfigObj

CONFIG_SPEC = ConfigObj("""
start = string(default="start")

[markdown]
extensions = string_list()
""", list_values=False)
