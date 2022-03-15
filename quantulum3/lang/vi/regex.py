#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod: Language specific regexes
"""

UNITS = [
    "không",
    "một",
    "hai",
    "ba",
    "bốn",
    "năm",
    "sáu",
    "bảy",
    "tám",
    "chín",
    "mười",
    "mười_một",
    "mười_hai",
    "mười_ba",
    "mười_bốn",
    "mười_lăm",
    "mười_sáu",
    "mười_bảy",
    "mười_tám",
    "mười_chín",
]

TENS = [
    "",
    "",
    "hai_mươi",
    "ba_mươi",
    "bốn_mươi",
    "năm_mươi",
    "sáu_mươi",
    "bảy_mươi",
    "tám_mươi",
    "chín_mươi",
]

SCALES = ["trăm", ["nghìn", "ngàn"], "triệu", ["tỷ", "tỉ"], ["nghìn_tỷ", "ngàn_tỷ", "nghìn_tỉ", "ngàn_tỉ"]]

DECIMALS = {
    "một_phần_hai": 0.5,
    "một_phần_ba": 1 / 3,
    "một_phần_tư": 0.25,
    "một_phần_năm": 0.2,
    "một_phần_sáu": 1 / 6,
    "một_phần_bảy": 1 / 7,
    "một_phần_tám": 1 / 8,
    "một_phần_chín": 1 / 9,
}

MISCNUM = {"&": (1, 0), "và": (1, 0)}

###############################################################################

SUFFIXES = {"k": 1e3, "K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}

MULTIPLICATION_OPERATORS = {" lần "}

DIVISION_OPERATORS = {u" mỗi ", u" trên ", u"per"}

GROUPING_OPERATORS = {u",", u" "}
DECIMAL_OPERATORS = {u"."}

# Pattern for extracting word based numbers
TEXT_PATTERN = r"""            # Pattern for extracting mixed digit-spelled num
    (?:
        (?<![a-zA-Z0-9+.-])    # lookbehind, avoid "Area51"
        {number_pattern_no_groups}
    )?
    [, ]?(?:{numberwords_regex})
    (?:[, -]*(?:{numberwords_regex}))*
    (?!\s?{number_pattern_no_groups}) # Disallow being followed by only a
                                      # number
"""

RANGES = {"đến", "tới"}
UNCERTAINTIES = {"cộng trừ", "xấp xỉ"}

POWERS = {"vuông": 2, "khối": 3}
EXPONENTS_REGEX = r"(?:(?:\^?\-?[0-9{{superscripts}}]+)?(?:\ (?:{powers}))?)".format(
    powers="|".join(POWERS.keys())
)
