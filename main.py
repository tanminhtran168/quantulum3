from quantulum3 import parser
import re

if __name__ == '__main__':
    quants = parser.parse("2 km/s", has_value=False)
    for quant in quants:
        print(quant.value, quant.unit)