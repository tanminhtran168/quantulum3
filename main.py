from quantulum3 import parser
import re

if __name__ == '__main__':
    quants = parser.parse("12m - 15m, 125km/h", has_value=True)
    for quant in quants:
        # if quant.unit.name != 'dimensionless':
        print(quant.value, quant.unit, quant.uncertainty)
    # print(re.match(r"", "300-"))