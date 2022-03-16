#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` unit and entity loading functions.
"""

import json
import os
from builtins import open
from collections import defaultdict

import inflect

from ... import load, const
from . import lang


###############################################################################
def build_common_words():
    # Read raw 4 letter file
    path = os.path.join(const.TOP_DIR, "common-units.txt")
    with open(path, "r", encoding="utf-8") as file:
        common_units = {line.strip() for line in file if not line.startswith("#")}
    path = os.path.join(const.TOP_DIR, "data/common-words.txt")
    words = defaultdict(list)  # Collect words based on length
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("#"):
                continue
            line = line.rstrip()
            if (
                line not in load.units(lang).surfaces_lower
                and line not in load.units(lang).symbols
                and line not in common_units
            ):
                words[len(line)].append(line)
    return words


###############################################################################
def load_common_words():
    path = os.path.join(const.TOP_DIR, "common-words.json")
    dumped = {}
    try:
        with open(path, "r", encoding="utf-8") as file:
            dumped = json.load(file)
    except OSError:  # pragma: no cover
        pass

    words = defaultdict(list)  # Collect words based on length
    for length, word_list in dumped.items():
        words[int(length)] = word_list
    return words


COMMON_WORDS = load_common_words()

