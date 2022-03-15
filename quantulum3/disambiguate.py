# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` disambiguation functions.
"""
from . import load, const


###############################################################################
def disambiguate_unit(unit_surface, lang=const.LANG):
    """
    Resolve ambiguity between units with same names, symbols or abbreviations.
    returns (str) unit name of the resolved unit
    """
    try:
        base = (
                load.units(lang).symbols[unit_surface]
                or load.units(lang).surfaces[unit_surface]
                or load.units(lang).surfaces_lower[unit_surface.lower()]
                or load.units(lang).symbols_lower[unit_surface.lower()]
        )
        if len(base) > 1:
            # base = no_clf.disambiguate_no_classifier(base, text, lang)
            base = sorted(base, key=lambda x: x.name)[0]
        elif len(base) == 1:
            base = next(iter(base))

        if base:
            base = base.name
        else:
            base = "unk"
    except KeyError:
        base = None

    return base


###############################################################################
def disambiguate_entity(key, lang=const.LANG):
    """
    Resolve ambiguity between entities with same dimensionality.
    """
    try:
        derived = sorted(load.entities(lang).derived[key], key=lambda x: x.name)
        if len(derived) > 1:
            # ent = no_clf.disambiguate_no_classifier(derived, text, lang)
            ent = derived[0]
        elif len(derived) == 1:
            ent = next(iter(derived))
        else:
            ent = None
    except (KeyError, StopIteration):
        ent = None

    return ent
