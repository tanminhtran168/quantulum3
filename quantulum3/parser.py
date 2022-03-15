#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` parser.
"""
import quantulum3 as q
import json
import re
from collections import defaultdict
from fractions import Fraction
from typing import List, Any

from . import classes as cls
from . import disambiguate as dis
from . import language, load, const
from . import regex as reg


def _get_parser(lang=const.LANG):
    """
    Get parser module for given language
    :param lang:
    :return:
    """
    return language.get("parser", lang)


###############################################################################
def extract_spell_out_values(text, lang=const.LANG):
    """
    Convert spelled out numbers in a given text to digits.
    """
    return _get_parser(lang).extract_spell_out_values(text)


###############################################################################
def substitute_values(text, values):
    """
    Convert spelled out numbers in a given text to digits.
    """

    shift, final_text, shifts = 0, text, defaultdict(int)
    for value in values:
        first = value["old_span"][0] + shift
        second = value["old_span"][1] + shift
        final_text = final_text[0:first] + value["new_surface"] + final_text[second:]
        shift += len(value["new_surface"]) - len(value["old_surface"])
        for char in range(first + 1, len(final_text)):
            shifts[char] = shift

    return final_text, shifts


###############################################################################
def get_values(item, lang=const.LANG):
    """
    Extract value from regex hit.
    """

    def callback(pattern):
        return " %s" % (reg.unicode_fractions()[pattern.group(0)])

    fractions = r"|".join(reg.unicode_fractions())

    value = item.group("value")
    # Remove grouping operators
    value = re.sub(
        r"(?<=\d)[%s](?=\d{3})" % reg.grouping_operators_regex(lang), "", value
    )
    # Replace unusual exponents by e (including e)
    value = re.sub(
        r"(?<=\d)(%s)(e|E|10)\^?" % reg.multiplication_operators_regex(lang), "e", value
    )
    # calculate other exponents
    value, factors = resolve_exponents(value)

    value = re.sub(fractions, callback, value, re.IGNORECASE)

    range_separator = re.findall(
        r"\d+ ?((?:-\ )?(?:%s)) ?\d" % "|".join(reg.ranges(lang)), value
    )
    uncertain_separator = re.findall(
        r"\d+ ?(%s) ?\d" % "|".join(reg.uncertainties(lang)), value
    )
    fraction_separator = re.findall(r"\d+/\d+", value)

    value = re.sub(" +", " ", value)
    uncertainty = None
    if range_separator:
        # A range just describes an uncertain quantity
        values = value.split(range_separator[0])
        values = [
            float(re.sub(r"-$", "", v)) * factors[i] for i, v in enumerate(values)
        ]
        if values[1] < values[0]:
            raise ValueError(
                "Invalid range, with second item being smaller than the first " "item"
            )
        mean = sum(values) / len(values)
        uncertainty = mean - min(values)
        values = [mean]
    elif uncertain_separator:
        values = [float(i) for i in value.split(uncertain_separator[0])]
        uncertainty = values[1] * factors[1]
        values = [values[0] * factors[0]]
    elif fraction_separator:
        values = value.split()
        try:
            if len(values) > 1:
                values = [float(values[0]) * factors[0] + float(Fraction(values[1]))]
            else:
                values = [float(Fraction(values[0]))]
        except ZeroDivisionError as e:
            raise ValueError("{} is not a number".format(values[0]), e)
    else:
        values = [float(re.sub(r"-$", "", value)) * factors[0]]

    return uncertainty, values


###############################################################################
def resolve_exponents(value, lang=const.LANG):
    """Resolve unusual exponents (like 2^4) and return substituted string and
       factor

    Params:
        value: str, string with only one value
    Returns:
        str, string with basis and exponent removed
        array of float, factors for multiplication

    """
    factors = []
    matches = re.finditer(
        reg.number_pattern_groups(lang), value, re.IGNORECASE | re.VERBOSE
    )
    for item in matches:
        if item.group("base") and item.group("exponent"):
            base = item.group("base")
            exp = item.group("exponent")
            if base in ["e", "E"]:
                # already handled by float
                factors.append(1)
                continue
                # exp = '10'
            # Expect that in a pure decimal base,
            # either ^ or superscript notation is used
            if re.match(r"\d+\^?", base):
                if not (
                        "^" in base
                        or re.match(r"[%s]" % reg.unicode_superscript_regex(), exp)
                ):
                    factors.append(1)
                    continue
            for superscript, substitute in reg.unicode_superscript().items():
                exp.replace(superscript, substitute)
            exp = float(exp)
            base = float(base.replace("^", ""))
            factor = base ** exp
            stripped = str(value).replace(item.group("scale"), "")
            value = stripped
            factors.append(factor)
        else:
            factors.append(1)
            continue
    return value, factors


###############################################################################
def build_unit_name(dimensions, lang=const.LANG):
    """
    Build the name of the unit from its dimensions.
    """
    name = _get_parser(lang).name_from_dimensions(dimensions)
    return name


###############################################################################
def get_conversion_from_dimensions(dimensions, lang='vi'):
    try:
        conversion_dict = []
        res = 1
        unit_dict = load.units(lang).unit_dict
        for dimension in dimensions:
            unit_label = dimension['base']
            si_label, factor = unit_dict[unit_label]['conversion'].values()
            dim = dimension['power']

            # TODO handle X/litre: Entity(litre) = volume, si_label = cubic metre
            if len(si_label.split()) == 2:
                if 'square' in si_label:
                    si_label = si_label.split()[1]
                    dim *= 2
                if 'cubic' in si_label:
                    si_label = si_label.split()[1]
                    dim *= 3

            conversion_dict.append({"base": si_label, "power": dim})
            res = res * (factor ** dim)
        # print(conversion_dict)
        si_units = json.load(open("quantulum3/data/si_units.json"))
        for si, value in si_units.items():
            if value == conversion_dict:
                return {"silabel": si, "factor": res}
    except KeyError:
        return None


def get_unit_from_dimensions(dimensions, text, lang=const.LANG):
    """
    Reconcile a unit based on its dimensionality.
    """
    key = load.get_key_from_dimensions(dimensions)

    try:
        unit = load.units(lang).derived[key]
        if unit.conversion is not None:
            if len(unit.conversion) == 0:
                unit.conversion = get_conversion_from_dimensions(dimensions)

    except KeyError:
        unit = cls.Unit(
            name=build_unit_name(dimensions, lang),
            dimensions=dimensions,
            entity=get_entity_from_dimensions(dimensions, text, lang),
            conversion=get_conversion_from_dimensions(dimensions)
        )
    # Carry on original composition
    unit.original_dimensions = dimensions
    return unit


def name_from_dimensions(dimensions, lang=const.LANG):
    """
    Build the name of a unit from its dimensions.
    Param:
        dimensions: List of dimensions
    """
    return _get_parser(lang).name_from_dimensions(dimensions)


def infer_name(unit):
    """
    Return unit name based on dimensions
    :return: new name of this unit
    """
    name = name_from_dimensions(unit.dimensions) if unit.dimensions else None
    return name


###############################################################################
def get_entity_from_dimensions(dimensions, text, lang=const.LANG):
    """
    Infer the underlying entity of a unit (e.g. "volume" for "m^3") based on
    its dimensionality.
    """

    new_derived = [
        {"base": load.units(lang).names[i["base"]].entity.name, "power": i["power"]}
        for i in dimensions
    ]

    # print(load.entities(lang).derived[(('mass', 1), ('volume', -1))])
    final_derived = []
    for der in new_derived:
        # TODO handle {'base': length, 'power': -3} --> {'base': volume, 'power': -1}
        entity = sorted(load.entities(lang).derived[((der['base'], abs(der['power'])),)], key=lambda x: x.name)
        if len(entity):
            der = {
                'base': list(entity)[0].name,
                'power': der['power'] // abs(der['power'])
            }
        final_derived.append(der)

    final_derived = sorted(final_derived, key=lambda x: x["base"])
    key = load.get_key_from_dimensions(final_derived)
    ent = dis.disambiguate_entity(key, lang)

    if ent is None:
        ent = cls.Entity(name="unknown", dimensions=new_derived)
    return ent


###############################################################################
def parse_unit(item, unit, slash, lang=const.LANG):
    """
    Parse surface and power from unit text.
    """
    return _get_parser(lang).parse_unit(item, unit, slash)


###############################################################################
def get_unit(item, text, lang=const.LANG):
    """
    Extract unit from regex hit.
    """
    group_units = ["prefix", "unit1", "unit2", "unit3", "unit4"]
    group_operators = ["operator1", "operator2", "operator3", "operator4"]
    # How much of the end is removed because of an "incorrect" regex match
    unit_shortening = 0

    item_units = [item.group(i) for i in group_units if item.group(i)]

    if len(item_units) == 0:
        unit = load.units(lang).names["dimensionless"]
    else:
        derived: List[Any]
        derived, slash = [], False
        multiplication_operator = False
        for index in range(0, 5):
            unit = item.group(group_units[index])
            operator_index = None if index < 1 else group_operators[index - 1]
            operator = None if index < 1 else item.group(operator_index)

            # disallow spaces as operators in units expressed in their symbols
            # Enforce consistency among multiplication and division operators
            # Single exceptions are colloquial number abbreviations (5k miles)
            if operator in reg.multiplication_operators(lang) or (
                    operator is None
                    and unit
                    and not (index == 1 and unit in reg.suffixes(lang))
            ):
                if multiplication_operator != operator and not (
                        index == 1 and str(operator).isspace()
                ):
                    if multiplication_operator is False:
                        multiplication_operator = operator
                    else:
                        # Cut if inconsistent multiplication operator
                        # treat the None operator differently - remove the
                        # whole word of it
                        if operator is None:
                            # For this, use the last consistent operator
                            # (before the current) with a space
                            # which should always be the preceding operator
                            derived.pop()
                            operator_index = group_operators[index - 2]
                        # Remove (original length - new end) characters
                        unit_shortening = item.end() - item.start(operator_index)
                        break

            # Determine whether a negative power has to be applied to following
            # units
            if operator and not slash:
                slash = any(i in operator for i in reg.division_operators(lang))
            # Determine which unit follows
            if unit:
                unit_surface, power = parse_unit(item, unit, slash, lang)
                base = dis.disambiguate_unit(unit_surface, lang)

                derived += [{"base": base, "power": power, "surface": unit_surface}]

        unit = get_unit_from_dimensions(derived, text, lang)
    return unit, unit_shortening


###############################################################################
def get_surface(shifts, orig_text, item, text, unit_shortening=0):
    """
    Extract surface from regex hit.
    """

    # handle cut end
    span = (item.start(), item.end() - unit_shortening)
    # extend with as many spaces as are possible (this is to handle cleaned text)
    i = span[1]
    while i < len(text) and text[i] == " ":
        i += 1
    span = (span[0], i)

    real_span = (span[0] - shifts[span[0]], span[1] - shifts[span[1] - 1])
    surface = orig_text[real_span[0]: real_span[1]]

    while any(surface.endswith(i) for i in [" ", "-"]):
        surface = surface[:-1]
        real_span = (real_span[0], real_span[1] - 1)

    while surface.startswith(" "):
        surface = surface[1:]
        real_span = (real_span[0] + 1, real_span[1])

    return surface, real_span


###############################################################################
def is_quote_artifact(orig_text, span):
    """
    Distinguish between quotes and units.
    """

    res = False
    cursor = re.finditer(r'["\'][^ .,:;?!()*+-].*?["\']', orig_text)

    for item in cursor:
        if span[0] <= item.span()[1] <= span[1]:
            res = item
            break

    return res


###############################################################################
def build_quantity(
        orig_text, text, item, values, unit, surface, span, uncert, lang=const.LANG,
):
    """
    Build a Quantity object out of extracted information.
    Takes care of caveats and common errors
    """
    return _get_parser(lang).build_quantity(
        orig_text, text, item, values, unit, surface, span, uncert
    )


###############################################################################
def clean_text(text, lang=const.LANG):
    """
    Clean text before parsing.
    """

    # Replace a few nasty unicode characters with their ASCII equivalent
    special_words = []
    special_words.extend([word.replace('_', ' ') for word in reg.units() if '_' in word])
    special_words.extend([word.replace('_', ' ') for word in reg.tens() if '_' in word])
    special_words.extend([word.replace('_', ' ') for word in reg.decimals() if '_' in word])
    for scale in reg.scales():
        if isinstance(scale, list):
            special_words.extend([word.replace('_', ' ') for word in scale if '_' in word])
        elif '_' in scale:
            special_words.append(scale.replace('_', ' '))

    for word in special_words:
        if word in text:
            text = text.replace(word, word.replace(' ', '_'))

    maps = {"×": "x", "–": "-", "−": "-"}
    for element in maps:
        text = text.replace(element, maps[element])

    # Language specific cleaning
    text = _get_parser(lang).clean_text(text)

    return text


###############################################################################
def parse(text, lang=const.LANG) -> List[cls.Quantity]:
    """
    Extract all quantities from unstructured text.
    """
    orig_text = text

    text = clean_text(text, lang)
    values = extract_spell_out_values(text, lang)
    text, shifts = substitute_values(text, values)

    quantities = []
    for item in reg.units_regex(lang).finditer(text):

        groups = dict([i for i in item.groupdict().items() if i[1] and i[1].strip()])

        try:
            uncertain, values = get_values(item, lang)

            unit, unit_shortening = get_unit(item, text)
            surface, span = get_surface(shifts, orig_text, item, text, unit_shortening)
            objs = build_quantity(
                orig_text, text, item, values, unit, surface, span, uncertain, lang
            )
            if objs is not None:
                quantities += objs
        except ValueError as err:
            print("Could not parse quantity: %s", err)

    return quantities


###############################################################################
def inline_parse(text):  # pragma: no cover
    """
    Extract all quantities from unstructured text.
    """

    parsed = parse(text)

    shift = 0
    for quantity in parsed:
        index = quantity.span[1] + shift
        to_add = u" {" + str(quantity) + u"}"
        text = text[0:index] + to_add + text[index:]
        shift += len(to_add)

    return text
