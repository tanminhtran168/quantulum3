#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` parser.
"""

import re
from importlib import import_module
from pathlib import Path
from . import const


###############################################################################
def languages():
    sub_dirs = [
        x
        for x in const.TOP_DIR.joinpath("lang").iterdir()
        if x.is_dir() and not x.name.startswith("__")
    ]
    langs = dict((x.name.lower(), x.name) for x in sub_dirs)
    langs.update((x.name[:2].lower(), x.name) for x in sub_dirs)
    return langs


# Not to be used directly, use subdir
SUB_DIRS = languages()
# Set of all supported languages
LANGUAGES = SUB_DIRS.keys()


def subdir(lang=const.LANG):
    # convert to language string
    lang = re.sub(r"[\s\-]", "_", lang).lower()
    try:
        # search for correct submodule
        sub_dirs = SUB_DIRS[lang]
    except KeyError:
        raise NotImplementedError("Unsupported language: {}".format(lang))
    return sub_dirs


###############################################################################
def get(module, lang=const.LANG):
    """
    Get module for given language
    :param module:
    :param lang:
    :return:
    """

    module = import_module(
        ".lang.{}.{}".format(subdir(lang), module), package=__package__
    )
    return module


###############################################################################
def top_dir(lang=const.LANG):
    return const.TOP_DIR.joinpath("lang", subdir(lang))
