import math
from service.fake_api_results import ALL_TITLES, OFFICIAL_COPY_RESULT, TITLE_RESULT

SEARCH_RESULTS_PER_PAGE = 20

def get_title(title_number):
    return TITLE_RESULT


def _get_titles(page_number):
    nof_results = len(ALL_TITLES)
    number_pages = math.ceil(nof_results / SEARCH_RESULTS_PER_PAGE)
    start_index = page_number * SEARCH_RESULTS_PER_PAGE
    end_index = start_index + SEARCH_RESULTS_PER_PAGE
    return {
        'number_pages': number_pages,
        'number_results': nof_results,
        'page_number': page_number,
        'titles': ALL_TITLES[start_index:end_index],
    }

def get_titles_by_postcode(postcode, page_number):
    return _get_titles(page_number)


def get_titles_by_address(address, page_number):
    return _get_titles(page_number)


def get_official_copy_data(title_number):
    return OFFICIAL_COPY_RESULT
