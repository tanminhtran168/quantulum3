import re
import json
import const
from wikidata.client import Client


def create_file_with_conversion():
    units = json.load(open(const.GENERAL_UNITS_PATH, encoding='utf-8'))
    vi_units = json.load(open(const.LANG_UNITS_OLD_PATH, encoding='utf-8'))
    conversions = json.load(open(const.CONVERSION_CONFIG_PATH, encoding='utf-8'))

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
    with open(const.LANG_UNITS_PATH, "w", encoding='utf-8') as f:
        json.dump(vi_units, f, ensure_ascii=False)


def create_si_unit_list():
    conversions = json.load(open(const.CONVERSION_CONFIG_PATH, encoding='utf-8'))
    units = json.load(open(const.LANG_UNITS_PATH, encoding='utf-8'))
    si_units = {}

    for conversion in conversions.values():
        si_unit = conversion["siLabel"]
        if si_unit == conversion["label"]:

            # create id
            si_units[si_unit] = {}
            si_units[si_unit]['id'] = conversion["unit"]

            # create dimensions
            power = 1
            words = si_unit.split(" ")
            dimensions = []
            for i, word in enumerate(words):
                if word in ['per', 'reciprocal']:
                    power = -1
                elif word in units:
                    if words[i - 1] == 'square':
                        dimensions.append({'base': word, 'power': 2 * power})
                    elif words[i - 1] == 'cubic':
                        dimensions.append({'base': word, 'power': 3 * power})
                    else:
                        dimensions.append({'base': word, 'power': power})
            si_units[si_unit]['dimensions'] = dimensions

    with open(const.SI_UNITS_PATH, "w", encoding='utf-8') as f:
        json.dump(si_units, f, ensure_ascii=False)


def parse_dimensions(math_symbols):
    """
    Parse the math_symbols with format: \mathsf{L}^2\mathsf{M}^{-2}
    """
    symbol2unit = {
        'L': 'length',
        'M': 'mass',
        'T': 'time',
        'I': 'current',
        'N': 'amount of substance',
        'J': 'luminous intensity',
        '\Theta': 'temperature'
    }
    dimension_dict = []

    # preprocess math_symbols
    math_symbols = math_symbols.replace('{', '')
    math_symbols = math_symbols.replace('}', '')
    math_symbols = math_symbols.replace(' ', '')

    ids = [d.start() for d in re.finditer(r'\\mathsf', math_symbols)]
    for i, index in enumerate(ids):
        if i < len(ids) - 1:
            end = ids[i+1]
        else:
            end = len(math_symbols)

        # dimension with no power
        power = 1
        if '^' not in math_symbols[index+6:end]:
            base = symbol2unit[math_symbols[index+7:end]]

        # dimension with power
        else:
            start = math_symbols.find('^', index)
            base = symbol2unit[math_symbols[index+7:start]]
            power = int(math_symbols[start+1:end])

        dimension_dict.append({'base': base, 'power': power})
    return dimension_dict


def get_si_entity_list():
    client = Client()
    si_units = json.load(open(const.SI_UNITS_PATH))
    entities = {}
    for unit in si_units.values():
        # get all relations in for this unit
        try:
            entities_data = client.get(unit['id'], load=True).data['claims']['P111']
            for ent in entities_data:
                ent_id = ent['mainsnak']['datavalue']['value']['id']
                ent = client.get(ent_id, load=True)
                label = str(ent.label)
                if label not in entities:
                    print(f"\nExtracting {label}")
                    e = {
                        'aliases': [label],
                        'description': str(ent.description),
                        'dimensions': []
                    }

                    # english aliases
                    if ent.data['aliases'].get('en'):
                        aliases = ent.data['aliases']['en']
                        if isinstance(aliases, dict):
                            e['aliases'].append(aliases['value'])
                        else:
                            e['aliases'].extend([a['value'] for a in aliases])

                    # vietnamese labels
                    if ent.data['labels'].get('vi'):
                        labels = ent.data['labels']['vi']
                        if isinstance(labels, dict):
                            e['aliases'].append(labels['value'])
                        else:
                            e['aliases'].extend([s['value'] for s in labels])

                    # vietnamese aliases
                    if ent.data['aliases'].get('vi'):
                        aliases = ent.data['aliases']['vi']
                        if isinstance(aliases, dict):
                            e['aliases'].append(aliases['value'])
                        else:
                            e['aliases'].extend([s['value'] for s in aliases])

                    # dimensions
                    if ent.data['claims'].get('P4020'):
                        e['dimensions'] = parse_dimensions(ent.data['claims']['P4020'][0]['mainsnak']['datavalue']['value'])
                    entities[label] = e
        except (KeyError, IndexError):
            pass

    with open(const.GENERAL_SI_ENTITIES_PATH, "w", encoding='utf-8') as f:
        json.dump(entities, f, ensure_ascii=False)


def check_entities():
    pass


if __name__ == '__main__':
    check_entities()