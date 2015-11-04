from service import address_utils, app, title_utils

MORE_PROPRIETOR_DETAILS = True


# TODO: test now that the formatting can be tested independently
def format_display_json(title_json):
    proprietors = _format_proprietors(title_json['data']['proprietors'])
    title_data = title_json['data']
    address_lines = address_utils.get_address_lines(title_data['address'])
    indexPolygon = _get_property_address_index_polygon(title_json['geometry_data'])

    title = {
        'number': title_json['title_number'],
        'last_changed': title_data.get('last_application_timestamp', 'No data'),
        'address_lines': address_lines,
        'proprietors': proprietors,
        'tenure': title_data.get('tenure', 'No data'),
        'indexPolygon': indexPolygon,
        'is_caution_title': title_utils.is_caution_title(title_data),
    }

    if 'lenders' in title_data:
        title['lenders'] = _format_proprietors(title_data['lenders'])
    if 'ppi_data' in title_data:
        title['ppi_data'] = _format_ppi_data(title_data)

    return title


def _format_ppi_data(title_data):
    # Remove period from end of PPI text if present
    return title_data['ppi_data'].rstrip('.')


def _format_proprietors(proprietors_data):
    return [_format_proprietor(proprietor) for proprietor in proprietors_data]


def _format_proprietor(proprietor):
    return {
        'name': _get_proprietor_name(proprietor),
        'name_extra_info': _get_proprietor_name_extra_info(proprietor),
        'addresses': _get_proprietor_addresses(proprietor),
    }


def _get_proprietor_name(proprietor):
    name = proprietor.get('name') or {}

    if name:
        if 'non_private_individual_name' in name:
            return name['non_private_individual_name']
        elif 'forename' in name or 'surname' in name:
            return _format_private_individual_name(name)
        else:
            raise Exception("Proprietor doesn't have name information")
    else:
        raise Exception("Proprietor doesn't have 'name' element")


def _get_proprietor_name_extra_info(proprietor):
    if MORE_PROPRIETOR_DETAILS:
        name = proprietor.get('name') or {}
        extra_info = ''

        if 'name_supplimentary' in name:
            extra_info += ', ' + name['name_supplimentary']
        if 'name_information' in name:
            extra_info += ', ' + name['name_information']
        if 'trading_name' in name:
            extra_info += ' trading as ' + name['trading_name']
        if 'non_private_individual_name' in name and 'country_incorporation' in name:
            extra_info += ' incorporated in ' + name['country_incorporation']

        return extra_info
    else:
        return ''


def _get_proprietor_addresses(proprietor):
    addresses = proprietor.get('addresses') or []
    return [{"lines": address_utils.get_address_lines(address)} for address in addresses]


# This method attempts to retrieve the index polygon data for the entry
def _get_property_address_index_polygon(geometry_data):
    index_polygon = None
    if geometry_data and ('index' in geometry_data):
        index_polygon = geometry_data['index']
    return index_polygon


def _format_private_individual_name(name):
    name_list = [name[field] for field in ['forename', 'surname'] if field in name]

    formatted_name = ' '.join(name_list)
    decoration = name.get('decoration')
    return '{0}, {1}'.format(formatted_name, decoration) if decoration else formatted_name
