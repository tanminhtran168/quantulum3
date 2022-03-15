quantulum3
==========
 [![Travis master build state](https://app.travis-ci.com/nielstron/quantulum3.svg?branch=master "Travis master build state")](https://app.travis-ci.com/nielstron/quantulum3)
 [![Coverage Status](https://coveralls.io/repos/github/nielstron/quantulum3/badge.svg?branch=master)](https://coveralls.io/github/nielstron/quantulum3?branch=master)
 [![PyPI version](https://badge.fury.io/py/quantulum3.svg)](https://pypi.org/project/quantulum3/)
 ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/quantulum3.svg)
 [![PyPI - Status](https://img.shields.io/pypi/status/quantulum3.svg)](https://pypi.org/project/quantulum3/)
 
Python library for information extraction of quantities, measurements
and their units from unstructured text. It is able to disambiguate between similar
looking units based on their *k-nearest neighbours* in their [GloVe](https://nlp.stanford.edu/projects/glove/) vector representation
and their [Wikipedia](https://en.wikipedia.org/) page.

This is the Python 3 compatible fork of [recastrodiaz\'
fork](https://github.com/recastrodiaz/quantulum) of [grhawks\'
fork](https://github.com/grhawk/quantulum) of [the original by Marco
Lagi](https://github.com/marcolagi/quantulum).
The compatibility with the newest version of sklearn is based on
the fork of [sohrabtowfighi](https://github.com/sohrabtowfighi/quantulum).

Installation
------------

First, install [`numpy`](https://pypi.org/project/numpy/), [`scipy`](https://www.scipy.org/install.html) and [`sklearn`](http://scikit-learn.org/stable/install.html).
Quantulum would still work without those packages, but it wouldn\'t be able to
disambiguate between units with the same name (e.g. *pound* as currency
or as unit of mass).

Then,

```bash
$ pip install quantulum3
```

Usage
-----

```pycon
>>> from quantulum3 import parser
>>> quants = parser.parse('I want 2 liters of wine')
>>> quants
[Quantity(2, 'litre')]
```

The *Quantity* class stores the surface of the original text it was
extracted from, as well as the (start, end) positions of the match:

```pycon
>>> quants[0].surface
u'2 liters'
>>> quants[0].span
(7, 15)
```

The *value* attribute provides the parsed numeric value and the *unit.name*
attribute provides the name of the parsed unit:

```pycon
>>> quants[0].value
2.0
>>> quants[0].unit.name
'litre'
```

An inline parser that embeds the parsed quantities in the text is also
available (especially useful for debugging):

```pycon
>>> print parser.inline_parse('I want 2 liters of wine')
I want 2 liters {Quantity(2, "litre")} of wine
```

As the parser is also able to parse dimensionless numbers,
this library can also be used for simple number extraction.

```pycon
>>> print parser.parse('I want two')
[Quantity(2, 'dimensionless')]
```

Units and entities
------------------

All units (e.g. *litre*) and the entities they are associated to (e.g.
*volume*) are reconciled against WikiPedia:

```pycon
>>> quants[0].unit
Unit(name="litre", entity=Entity("volume"), uri=https://en.wikipedia.org/wiki/Litre)

>>> quants[0].unit.entity
Entity(name="volume", uri=https://en.wikipedia.org/wiki/Volume)
```

This library includes more than 290 units and 75 entities. It also
parses spelled-out numbers, ranges and uncertainties:

```pycon
>>> parser.parse('I want a gallon of beer')
[Quantity(1, 'gallon')]

>>> parser.parse('The LHC smashes proton beams at 12.8–13.0 TeV')
[Quantity(12.8, "teraelectronvolt"), Quantity(13, "teraelectronvolt")]

>>> quant = parser.parse('The LHC smashes proton beams at 12.9±0.1 TeV')
>>> quant[0].uncertainty
0.1
```

Non-standard units usually don\'t have a WikiPedia page. The parser will
still try to guess their underlying entity based on their
dimensionality:

```pycon
>>> parser.parse('Sound travels at 0.34 km/s')[0].unit
Unit(name="kilometre per second", entity=Entity("speed"), uri=None)
```


Unit conversion
------------------
Convert units and compound units to the corresponding SI unit. 
The SI unit list and conversion rate are crawled from Wikidata.

This library contains 154 SI units and 1688 conversion configurations
```pycon
>>> parser.parse('I want a gallon of beer')
[Quantity(58, "Unit(name="kilometre per hour", entity=Entity("speed"), 
conversion=Conversion("{'silabel': 'metre per second', 'factor': 0.2777777777777778}"))")]
```
