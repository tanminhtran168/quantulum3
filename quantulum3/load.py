#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` unit and entity loading functions.
"""
import quantulum3 as q
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, List, Tuple, Union

from . import language, classes, const


###############################################################################
_CACHE_DICT = {}


def cached(funct):
    """
    Decorator for caching language specific data
    :param funct: the method, dynamically responding to language. Only
                  parameter is lang
    :return: the method, dynamically responding to language but also caching
             results
    """
    assert callable(funct)

    def cached_function(lang=const.LANG):
        try:
            return _CACHE_DICT[id(funct)][lang]
        except KeyError:
            result = funct(lang)
            _CACHE_DICT[id(funct)] = {lang: result}
            return result

    return cached_function


def object_pairs_hook_defer_duplicate_keys(object_pairs: List[Tuple[str, Any]]):
    keys = [x[0] for x in object_pairs]
    try:
        assert len(set(keys)) == len(keys)
    except AssertionError:
        raise AssertionError(
            "Dictionary has entries with same name: {}".format(
                [object_pairs[i] for i, k in enumerate(keys) if keys.count(k) > 1]
            )
        )
    return dict(object_pairs)


###############################################################################
# @cached
def _get_load(lang=const.LANG):
    return language.get("load", lang)

def _load_json(path_or_string: Union[Path, str]):
    if isinstance(path_or_string, Path):
        with path_or_string.open("r", encoding="utf-8") as jsonfile:
            return jsonfile.read()
    elif isinstance(path_or_string, str) and path_or_string.endswith(".json"):
        with open(path_or_string, "r", encoding="utf-8") as jsonfile:
            return jsonfile.read()
    return path_or_string


def _load_json_dict(path_or_string: Union[Path, str, dict]):
    if isinstance(path_or_string, dict):
        return path_or_string
    return json.loads(
        _load_json(path_or_string),
        object_pairs_hook=object_pairs_hook_defer_duplicate_keys,
    )


CUSTOM_ENTITIES = defaultdict(dict)
CUSTOM_UNITS = defaultdict(dict)

###############################################################################
METRIC_PREFIXES = {
    "Y": (["yotta", "yôta", "yô-ta-"], 1e24),
    "Z": (["zetta", "zêta", "zê-ta-"], 1e21),
    "E": (["exa", "êxa", "ê-xa-"], 1e18),
    "P": (["peta", "pêta", "pê-ta-"], 1e15),
    "T": (["tera", "têra", "tê-ra-"], 1e12),
    "G": (["giga", "gi-ga-"], 1e9),
    "M": (["mega", "mêga", "mê-ga-"], 1e6),
    "k": (["kilo", "kilô", "ki-lô-"], 1e3),
    "h": (["hecto", "héctô", "héc-tô-"], 1e2),
    "da": (["deca", "deka", "đêca", "đề-ca-"], 10),
    "d": (["deci", "đêxi", "đề-xi-"], 1e-1),
    "c": (["centi", "xenti", "xăngti", "xen-ti-", "xăng-ti-"], 1e-2),
    "m": (["milli", "mili", "mi-li-"], 1e-3),
    "µ": (["micro", "micrô", "mi-crô-"], 1e-6),
    "n": (["nano", "nanô", "na-nô-"], 1e-9),
    "p": (["pico", "picô", "pi-cô-"], 1e-12),
    "f": (["femto", "femtô", "fem-tô-"], 1e-15),
    "a": (["atto", "atô", "a-tô-"], 1e-18),
    "z": (["zepto", "zeptô", "zep-tô-"], 1e-21),
    "y": (["yocto", "yóctô", "yóc-tô-"], 1e-24),
    "Ki": (["kibi"], 2e10),
    "Mi": (["mebi"], 2e20),
    "Gi": (["gibi"], 2e30),
    "Ti": (["tebi"], 2e40),
    "Pi": (["pebi"], 2e50),
    "Ei": (["exbi"], 2e60),
    "Zi": (["zebi"], 2e70),
    "Yi": (["yobi"], 2e80)
}


###############################################################################
def get_key_from_dimensions(derived):
    """
    Translate dimensionality into key for DERIVED_UNI and DERIVED_ENT dicts.
    """
    return tuple((i["base"], i["power"]) for i in derived)


###############################################################################
class Entities(object):
    def __init__(self, entity_dicts: List[Union[Path, str, dict]]):
        """
        Load entities from JSON file.
        """

        # Merge entity dictionary's
        all_entities = defaultdict(dict)
        for ed in entity_dicts:
            for new_name, new_ent in _load_json_dict(ed).items():
                all_entities[new_name].update(new_ent)

        self.names = dict(
            (
                name,
                classes.Entity(
                    name=name,
                    dimensions=props.get("dimensions", []),
                    uri=props.get("URI"),
                ),
            )
            for name, props in all_entities.items()
        )

        # Generate derived units
        derived_ent = defaultdict(set)
        for entity in self.names.values():
            if not entity.dimensions:
                continue
            perms = self.get_dimension_permutations(entity.dimensions)
            for perm in perms:
                key = get_key_from_dimensions(perm)
                derived_ent[key].add(entity)

        self.derived = derived_ent

    def get_dimension_permutations(self, derived):
        """
        Get all possible dimensional definitions for an entity.
        """

        new_derived = defaultdict(int)
        for item in derived:
            new = self.names[item["base"]].dimensions
            if new:
                for new_item in new:
                    new_derived[new_item["base"]] += new_item["power"] * item["power"]
            else:
                new_derived[item["base"]] += item["power"]

        final = [
            [{"base": i[0], "power": i[1]} for i in list(new_derived.items())],
            derived,
        ]
        final = [sorted(i, key=lambda x: x["base"]) for i in final]

        candidates = []
        for item in final:
            if item not in candidates:
                candidates.append(item)

        return candidates


@cached
def entities(lang=const.LANG):
    """
    Cached entity object
    """
    return Entities(
        [const.GENERAL_ENTITIES_PATH, const.LANG_ENTITIES_PATH, CUSTOM_ENTITIES]
    )


###############################################################################
def get_derived_units(names):
    """
    Create dictionary of unit dimensions.
    """

    derived_uni = {}

    for name in names:
        key = get_key_from_dimensions(names[name].dimensions)
        derived_uni[key] = names[name]
        plain_derived = [{"base": name, "power": 1}]
        key = get_key_from_dimensions(plain_derived)
        derived_uni[key] = names[name]
        if not names[name].dimensions:
            names[name].dimensions = plain_derived
        names[name].dimensions = [
            {"base": names[i["base"]].name, "power": i["power"]}
            for i in names[name].dimensions
        ]

    # print(derived_uni[(('kilogram', 1), ('metre', -3))])
    return derived_uni


###############################################################################
class Units(object):
    def __init__(self, unit_dict_json: List[Union[str, Path, dict]], lang=const.LANG):
        """
        Load units from JSON file.
        """
        # names of all units
        self.names = {}
        self.symbols, self.symbols_lower = defaultdict(set), defaultdict(set)
        self.surfaces, self.surfaces_lower = defaultdict(set), defaultdict(set)
        self.prefix_symbols = defaultdict(set)
        self.lang = lang
        self.unit_dict = None

        unit_dict = defaultdict(dict)
        for ud in unit_dict_json:
            for name, unit in _load_json_dict(ud).items():
                for _name, _unit in self.prefixed_units(name, unit):
                    # unit_dict[_name].update(_unit)
                    if unit_dict.get(_name) is None:
                        unit_dict[_name] = _unit
                    else:
                        surfaces = unit_dict[_name].get('surfaces', []).extend(_unit.get('surfaces', []))
                        if surfaces is not None:
                            unit_dict[_name]["surfaces"] = list(set(surfaces))
                        if _unit.get("conversion") is not None:
                            unit_dict[_name]["conversion"] = _unit["conversion"]

        for name, unit in unit_dict.items():
            self.load_unit(name, unit)

        self.unit_dict = unit_dict

        self.derived = get_derived_units(self.names)

        # symbols of all units
        self.symbols_all = self.symbols.copy()
        self.symbols_all.update(self.symbols_lower)

        # surfaces of all units
        self.surfaces_all = self.surfaces.copy()
        self.surfaces_all.update(self.surfaces_lower)

    def load_unit(self, name, unit):
        try:
            assert name not in self.names
        except AssertionError:  # pragma: no cover
            msg = "Two units with same name in units.json: %s" % name
            raise Exception(msg)

        obj = classes.Unit(
            name=name,
            surfaces=unit.get("surfaces", []),
            entity=entities().names[unit["entity"]],
            conversion=unit.get("conversion", []),
            uri=unit.get("URI"),
            symbols=unit.get("symbols", []),
            dimensions=unit.get("dimensions", []),
            currency_code=unit.get("currency_code"),
            lang=self.lang,
        )

        self.names[name] = obj

        for symbol in unit.get("symbols", []):
            self.symbols[symbol].add(obj)
            self.symbols_lower[symbol.lower()].add(obj)
            if unit["entity"] == "currency":
                self.prefix_symbols[symbol].add(obj)

        for surface in unit.get("surfaces", []):
            self.surfaces[surface].add(obj)
            self.surfaces_lower[surface.lower()].add(obj)

    @staticmethod
    def prefixed_units(name, unit):
        yield name, unit
        # If SI-prefixes are given, add them
        for prefix in unit.get("prefixes", []):
            assert (
                    prefix in METRIC_PREFIXES
            ), "Given prefix '{}' for unit '{}' not supported".format(prefix, name)
            assert (
                    len(unit["dimensions"]) <= 1
            ), "Prefixing not supported for multiple dimensions in {}".format(name)
            surfaces = []
            for prefix_mention in METRIC_PREFIXES[prefix][0]:
                surfaces.extend([prefix_mention + i for i in unit["surfaces"]])

            uri = METRIC_PREFIXES[prefix][0][0].capitalize() + unit["URI"].lower()
            # we usually do not want the "_(unit)" postfix for prefixed units
            uri = uri.replace("_(unit)", "")

            yield METRIC_PREFIXES[prefix][0][0] + name, {
                "surfaces": surfaces,
                "entity": unit["entity"],
                "URI": uri,
                "dimensions": [],
                "symbols": [prefix + i for i in unit["symbols"]],
                "conversion": {"silabel": name, "factor": METRIC_PREFIXES[prefix][1]}
            }


@cached
def units(lang=const.LANG):
    """
    Cached unit object
    """
    return Units([const.GENERAL_UNITS_PATH, const.LANG_UNITS_PATH, CUSTOM_UNITS], lang)


###############################################################################
@cached
def training_set(lang=const.LANG):
    training_set_ = []

    path = language.top_dir(lang).joinpath("train")
    for file in path.iterdir():
        if file.suffix == ".json":
            with file.open("r", encoding="utf-8") as train_file:
                training_set_ += json.load(train_file)

    return training_set_


###############################################################################
def add_custom_unit(name: str, **kwargs):
    """
    Adds a custom unit to the set of default units
    Note: causes a reload of all units
    :param name: Name of the unit to add, should preferably be unique,
    otherwise will overwrite attributes in existing units
    :param kwargs: properties of the unit as found in units.json, i.e. surfaces=["centimetre"]
    """
    CUSTOM_UNITS[name].update(kwargs)
    _CACHE_DICT.clear()


def remove_custom_unit(name: str):
    """
    Removes a unit from the set of custom units
    Note: causes a reload of all units
    :param name: Name of the unit to remove. This will not affect units that are loaded per default.
    """
    CUSTOM_UNITS.pop(name)
    _CACHE_DICT.clear()


def add_custom_entity(name: str, **kwargs):
    """
    Adds a custom entity to the set of default entities
    Note: causes a reload of all entities
    :param name: Name of the entity to add, should preferably be unique,
    otherwise will overwrite attributes in existing entities
    :param kwargs: properties of the entity as found in entities.json, i.e. surfaces=["centimetre"]
    """
    CUSTOM_ENTITIES[name].update(kwargs)
    _CACHE_DICT.clear()


def remove_custom_entity(name: str):
    """
    Removes an entity from the set of custom entities
    Note: causes a reload of all entities
    :param name: Name of the entity to remove. This will not affect entities that are loaded per default.
    """
    CUSTOM_ENTITIES.pop(name)
    _CACHE_DICT.clear()
