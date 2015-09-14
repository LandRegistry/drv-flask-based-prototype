import dateutil                       # type: ignore
import dateutil.parser                # type: ignore
import re

from service import title_utils

ALPHANUMERIC_CHARACTER_PATTERN = re.compile(r'[^a-zA-Z0-9_ ;:\-,\.()&£]+', re.UNICODE)


def format_date(value):
    return dateutil.parser.parse(value).strftime('%d %B %Y')


def format_time(value):
    return dateutil.parser.parse(value).strftime('%H:%M:%S')


def pluralize(number, singular='', plural='s'):
    if number == 1:
        return singular
    else:
        return plural


def check_date_existence(value):
    if not value:
        return 'Not Dated'
    else:
        return value


def get_tenure_info(title):
    if title_utils.is_caution_title(title['data']):
        return 'Caution against first registration'
    else:
        return title['data']['tenure']


def strip_illegal_characters(value):
    return re.sub(ALPHANUMERIC_CHARACTER_PATTERN, '', value)


def get_all_filters():
    return {
        'date': format_date,
        'time': format_time,
        'pluralize': pluralize,
        'check_date_existence': check_date_existence,
        'strip_illegal_characters': strip_illegal_characters,
        'tenure_info': get_tenure_info,
    }
