#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` classes.
"""

from typing import Any, Dict, List, Optional, Tuple
from . import const


###############################################################################
class Entity(object):
    """
    Class for an entity (e.g. "volume").
    """

    def __init__(
            self,
            name: str,
            dimensions: List[Dict[str, Any]] = [],
            uri: Optional[str] = None,
    ):

        self.name = name
        self.dimensions = dimensions
        self.uri = uri

    def __repr__(self):

        msg = 'Entity(name="%s", uri=%s)'
        msg = msg % (self.name, self.uri)
        return msg

    def __eq__(self, other):

        if isinstance(other, self.__class__):
            return self.name == other.name and self.dimensions == other.dimensions
        else:
            return False

    def __ne__(self, other):

        return not self.__eq__(other)

    def __hash__(self):

        return hash(repr(self))


###############################################################################
class Unit(object):
    """
    Class for a unit (e.g. "gallon").
    """

    def __init__(
            self,
            name: str,
            entity: Entity,
            conversion: dict,
            surfaces: List[str] = [],
            uri: Optional[str] = None,
            symbols: List[str] = [],
            dimensions: List[Dict[str, Any]] = [],
            currency_code: Optional[str] = None,
            original_dimensions: Optional[List[Dict[str, Any]]] = None,
            lang=const.LANG,
    ):
        """Initialization method."""
        self.name = name
        self.surfaces = surfaces
        self.entity = entity
        self.conversion = conversion
        self.uri = uri
        self.symbols = symbols
        self.dimensions = dimensions
        # Stores the untampered dimensions that were parsed from the text
        self.original_dimensions = original_dimensions
        self.currency_code = currency_code
        self.lang = lang

    def __repr__(self):

        msg = 'Unit(name="%s", entity=Entity("%s"), \nConversion("%s"))'
        msg = msg % (self.name, self.entity.name, self.conversion)
        return msg

    def __eq__(self, other):

        if isinstance(other, self.__class__):
            return (
                self.name == other.name
                and self.entity == other.entity
                and all(
                    dim1["base"] == dim2["base"] and dim1["power"] == dim2["power"]
                    for dim1, dim2 in zip(self.dimensions, other.dimensions)
                )
            )
        else:
            return False

    def __ne__(self, other):

        return not self.__eq__(other)

    def __hash__(self):

        return hash(repr(self))


###############################################################################


class Quantity(object):
    """
    Class for a quantity (e.g. "4.2 gallons").
    """

    def __init__(
            self,
            value: float,
            unit: Unit,
            surface: Optional[str] = None,
            span: Optional[Tuple[int, int]] = None,
            uncertainty: Optional[float] = None,
            lang="vi",
    ):

        self.value = value
        self.unit = unit
        self.surface = surface
        self.span = span
        self.uncertainty = uncertainty
        self.lang = lang

    def __repr__(self):

        msg = 'Quantity(%g, "%s")'
        msg = msg % (self.value, repr(self.unit))
        return msg

    def __eq__(self, other):

        if isinstance(other, self.__class__):
            return (
                    self.value == other.value
                    and self.unit == other.unit
                    and self.surface == other.surface
                    and self.span == other.span
                    and self.uncertainty == other.uncertainty
            )
        else:
            return False

    def __ne__(self, other):

        return not self.__eq__(other)

    def __str__(self):
        return self.to_spoken(self.lang)

    def to_spoken(self, lang=None):
        """
        Express quantity as a speakable string
        :return: Speakable version of this quantity
        """
        return speak.quantity_to_spoken(self, lang or self.lang)
