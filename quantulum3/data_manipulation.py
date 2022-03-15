import json


def create_file_with_conversion():
    units = json.load(open("data/units.json", encoding='utf-8'))
    vi_units = json.load(open("lang/vi/data/units.json", encoding='utf-8'))
    conversions = json.load(open(".data/unitConversionConfig.json", encoding='utf-8'))

    for unit in units:
        if vi_units.get(unit) is None:
            vi_units[unit] = units[unit]

    conversions = {
        v["label"]: {
            "silabel": v["siLabel"],
            "factor": float(v["factor"])
        } for v in conversions.values()}

    for unit in vi_units:
        if unit in conversions:
            vi_units[unit]["conversion"] = conversions[unit]

    json.dump(vi_units, open("lang/vi/data/unit_conversion.json", "w", encoding='utf-8'), ensure_ascii=False)


def create_si_unit_list():
    conversions = json.load(open(".data/unitConversionConfig.json", encoding='utf-8'))
    units = json.load(open("lang/vi/data/unit_conversion.json", encoding='utf-8'))
    si_units = {}
    for conversion in conversions.values():
        si_unit = conversion["siLabel"]
        if si_unit not in units:
            power = 1
            words = si_unit.split(" ")
            dimensions = []
            for i, word in enumerate(words):
                if word in ['per', 'reciprocal']:
                    power = -1
                elif word in units:
                    if words[i-1] == 'square':
                        dimensions.append({'base': word, 'power': 2 * power})
                    elif words[i-1] == 'cubic':
                        dimensions.append({'base': word, 'power': 3 * power})
                    else:
                        dimensions.append({'base': word, 'power': power})
            si_units[si_unit] = dimensions
        else:
            if units[si_unit]["dimensions"]:
                si_units[si_unit] = units[si_unit]["dimensions"]
            else:
                si_units[si_unit] = {'base': si_unit, 'power': 1}

    json.dump(si_units, open(".data/si_units.json", "w", encoding='utf-8'), ensure_ascii=False)


def get_si_entity_list():
    pass


if __name__ == '__main__':
    create_si_unit_list()
