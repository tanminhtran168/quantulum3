from pathlib import Path

TOP_DIR = Path(__file__).parent or Path("")
TOP_DIR_DATA = TOP_DIR.joinpath("data")

SI_UNITS_PATH = TOP_DIR_DATA.joinpath("si_units.json")
GENERAL_UNITS_PATH = TOP_DIR_DATA.joinpath("units.json")
GENERAL_ENTITIES_PATH = TOP_DIR_DATA.joinpath("entities.json")
CONVERSION_CONFIG_PATH = TOP_DIR_DATA.joinpath("conversion_config.json")
GENERAL_SI_ENTITIES_PATH = TOP_DIR_DATA.joinpath("si_entities.json")

LANG = 'vi'
LANG_TOP_DIR = TOP_DIR.joinpath("lang", LANG)
LANG_TOP_DIR_DATA = LANG_TOP_DIR.joinpath("data")

LANG_UNITS_OLD_PATH = LANG_TOP_DIR_DATA.joinpath("units.json")
LANG_UNITS_PATH = LANG_TOP_DIR_DATA.joinpath("unit_conversion.json")
LANG_ENTITIES_PATH = LANG_TOP_DIR_DATA.joinpath("entities.json")
