import re

BASIC_POSTCODE_REGEX = '^[A-Z]{1,2}[0-9R][0-9A-Z]? ?[0-9][A-Z]{2}$'
BASIC_POSTCODE_WITH_SURROUNDING_GROUPS_REGEX = (
    r'(?P<leading_text>.*\b)\s?'
    r'(?P<postcode>[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][A-Z]{2}\b)\s?'
    r'(?P<trailing_text>.*)'
)


def get_building_description_lines(address_data):
    lines = []
    if ('sub_building_description' in address_data and
            'sub_building_no' in address_data):
        lines.append(
            "{0} {1}".format(
                address_data['sub_building_description'],
                address_data['sub_building_no']))
    elif 'sub_building_description' in address_data:
        lines.append(address_data['sub_building_description'])
    elif 'sub_building_no' in address_data:
        lines.append(address_data['sub_building_no'])
    return lines


def get_street_name_lines(address_data):
    lines = []
    street_name_string = ""
    if 'house_no' in address_data or 'house_alpha' in address_data:
        street_name_string += "{0}{1}".format(
            address_data.get(
                'house_no', ''), address_data.get(
                'house_alpha', ''))
    if ('secondary_house_no' in address_data or
            'secondary_house_alpha' in address_data):
        secondary_string = "{0}{1}".format(
            address_data.get(
                'secondary_house_no', ''), address_data.get(
                'secondary_house_alpha', ''))
        if street_name_string:
            street_name_string += "-{0}".format(secondary_string)
        else:
            street_name_string += secondary_string
    if 'street_name' in address_data:
        street_name = address_data['street_name']
        if street_name_string:
            street_name_string += " {0}".format(street_name)
        else:
            street_name_string += street_name
    if street_name_string:
        lines.append(street_name_string)
    return lines


def get_address_lines(address_data):
    lines = []
    if address_data:
        address_type = address_data.get('address_type', None)
        if address_type == "DX":
            if ('care_of' in address_data or 'care_of_name' in address_data):
                lines.append(
                    "care of {0}".format(
                        address_data.get('care_of_name', ''))
                )
            lines.append(address_data.get('dx_no', None))
            lines.append(address_data.get('exchange_name', None))
        elif address_type == "ELECTRONIC":
            lines.append(address_data.get('email_address', None))
        elif address_type == "BFPO" or address_type == "FOREIGN":
            if ('care_of' in address_data or 'care_of_name' in address_data):
                lines.append(
                    "care of {0}".format(
                        address_data.get('care_of_name', ''))
                )
            lines.append(address_data.get('foreign_bfpo_address1', None))
            lines.append(address_data.get('foreign_bfpo_address2', None))
            lines.append(address_data.get('foreign_bfpo_address3', None))
            lines.append(address_data.get('foreign_bfpo_address4', None))
            lines.append(address_data.get('foreign_bfpo_address5', None))
            lines.append(address_data.get('foreign_bfpo_address6', None))
            lines.append(address_data.get('country', None))
        else:
            if ('care_of' in address_data or 'care_of_name' in address_data):
                lines.append(
                    "care of {0}".format(
                        address_data.get('care_of_name', ''))
                )
            lines.append(address_data.get('leading_info', None))
            lines += get_building_description_lines(address_data)
            lines.append(address_data.get('house_description', None))
            lines += get_street_name_lines(address_data)
            lines.append(address_data.get('street_name_2', None))
            lines.append(address_data.get('local_name', None))
            lines.append(address_data.get('local_name_2', None))
            lines.append(address_data.get('town', None))
            lines.append(address_data.get('postcode', None))
            lines.append(address_data.get('trail_info', None))
    non_empty_lines = [x for x in lines if x is not None]
    # If the JSON doesn't contain the individual fields non_empty_lines will be
    # empty
    # Check if this is the case and if their is an address_string
    if not non_empty_lines and address_data and address_data.get(
            'address_string'):
        non_empty_lines = format_address_string(
            address_data.get('address_string'))
    return non_empty_lines


def format_address_string(address_string):
    # remove brackets and split the address string on commas
    address_lines = re.sub('[\(\)]', '', address_string).split(', ')
    result = address_lines[:]
    # Strip leading and trailing whitespace and see if the last line is a just
    # a postcode
    last_line = address_lines[-1].strip()
    if not re.search(BASIC_POSTCODE_REGEX, last_line):
        # If not, remove the line from address_lines, splt out the postcode and
        # any preceeding text and trailing text and add them to address_lines
        # as separate lines (if they exist)
        del(address_lines[-1])
        matches = re.match(
            BASIC_POSTCODE_WITH_SURROUNDING_GROUPS_REGEX,
            last_line)
        if matches:
            if matches.group('leading_text') and len(
                    matches.group('leading_text').strip()) > 0:
                address_lines.append(matches.group('leading_text').strip())
            address_lines.append(matches.group('postcode').strip())
            if matches.group('trailing_text') and len(
                    matches.group('trailing_text').strip()) > 0:
                address_lines.append(matches.group('trailing_text').strip())
            result = address_lines
    return result
