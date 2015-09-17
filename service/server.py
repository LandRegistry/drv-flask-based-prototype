from datetime import datetime                                                                                   # type: ignore
from flask import abort, make_response, Markup, redirect, render_template, request, Response, session, url_for  # type: ignore
from flask_weasyprint import HTML, render_pdf                                                                   # type: ignore
import re

from service import address_utils, api_client, app, title_formatter, title_utils
from service.forms import AccountForm, PaymentForm, SigninForm, TitleSearchForm

TITLE_NUMBER_REGEX = re.compile('^([A-Z]{0,3}[1-9][0-9]{0,5}|[0-9]{1,6}[ZT])$')
POSTCODE_REGEX = re.compile(address_utils.BASIC_POSTCODE_REGEX)

USERNAME = 'Darcy Bloggs'


@app.route('/login', methods=['GET'])
def signin_page():
    return _login_page()


@app.route('/login', methods=['POST'])
def sign_in():
    title_number = request.args.get('title_number')
    display_page_number = int(request.args.get('page') or 1)
    search_term = request.args.get('search_term', title_number)

    form = SigninForm(csrf_enabled=False)

    if not form.validate():
        # entered invalid login form details so send back to same page with form error messages
        return _login_page(form)
    else:
        return redirect(url_for('payment_details', title_number=title_number, page=display_page_number, search_term=search_term))


@app.route('/logout', methods=['GET'])
def sign_out():
    return redirect(url_for('sign_in'))


@app.route('/titles/<title_number>', methods=['GET'])
def get_title(title_number):
    title = _get_register_title(title_number)

    if title:
        display_page_number = int(request.args.get('page') or 1)
        search_term = request.args.get('search_term', title_number)
        breadcrumbs = _breadcumbs_for_title_details(title_number, search_term, display_page_number)
        show_pdf = True
        full_title_data = None

        return _title_details_page(title, search_term, breadcrumbs, show_pdf, full_title_data)
    else:
        abort(404)


@app.route('/titles/<title_number>.pdf', methods=['GET'])
def display_title_pdf(title_number):
    title = _get_register_title(title_number)
    if title:
        full_title_data = api_client.get_official_copy_data(title_number)
        if full_title_data:
            sub_registers = full_title_data.get('official_copy_data', {}).get('sub_registers')
            if sub_registers:
                html = _create_pdf_template(sub_registers, title, title_number)
                return render_pdf(HTML(string=html))
    abort(404)


@app.route('/title-search', methods=['POST'])
@app.route('/title-search/<search_term>', methods=['POST'])
def find_titles():
    display_page_number = int(request.args.get('page') or 1)

    search_term = request.form['search_term'].strip()
    if search_term:
        return redirect(url_for('find_titles', search_term=search_term, page=display_page_number))
    else:
        # TODO: we should redirect to that page
        return _initial_search_page()


@app.route('/', methods=['GET'])
@app.route('/title-search', methods=['GET'])
@app.route('/title-search/<search_term>', methods=['GET'])
def find_titles_page(search_term=''):
    display_page_number = int(request.args.get('page') or 1)
    page_number = display_page_number - 1  # page_number is 0 indexed

    search_term = search_term.strip()
    if not search_term:
        return _initial_search_page()
    else:
        return _get_address_search_response(search_term, page_number)


def _get_register_title(title_number):
    title = api_client.get_title(title_number)
    return title_formatter.format_display_json(title) if title else None


def _get_address_search_response(search_term, page_number):
    search_term = search_term.upper()
    if _is_title_number(search_term):
        return _get_search_by_title_number_response(search_term, page_number)
    elif _is_postcode(search_term):
        return _get_search_by_postcode_response(search_term, page_number)
    else:
        return _get_search_by_address_response(search_term, page_number)


def _get_search_by_title_number_response(search_term, page_number):
    display_page_number = page_number + 1
    title_number = search_term
    title = _get_register_title(title_number)
    if title:
        # Redirect to the display_title method to display the digital register
        return redirect(url_for('get_which_documents', title_number=title_number,
                                page_number=display_page_number, search_term=search_term))
    else:
        # If title not found display 'no title found' screen
        results = {'number_results': 0}
        return _search_results_page(results, search_term)


def _get_search_by_postcode_response(search_term, page_number):
    postcode = _normalise_postcode(search_term)
    postcode_search_results = api_client.get_titles_by_postcode(postcode, page_number)
    return _search_results_page(postcode_search_results, postcode)


def _get_search_by_address_response(search_term, page_number):
    address_search_results = api_client.get_titles_by_address(search_term, page_number)
    return _search_results_page(address_search_results, search_term)


def _is_title_number(search_term):
    return TITLE_NUMBER_REGEX.match(search_term)


def _is_postcode(search_term):
    return POSTCODE_REGEX.match(search_term)


def _breadcumbs_for_title_details(title_number, search_term, display_page_number):
    search_breadcrumb = {'text': 'Search the land and property register', 'url': url_for('find_titles')}
    results_breadcrumb = {'text': 'Search results', 'url': url_for('find_titles_page', search_term=search_term,
                                                                   page=display_page_number)}
    current_breadcrumb = {'current': 'Viewing {}'.format(title_number)}

    found_title_by_number = title_number.lower() == search_term.lower()

    if found_title_by_number:
        return [search_breadcrumb, current_breadcrumb]
    else:
        return [search_breadcrumb, results_breadcrumb, current_breadcrumb]


def _normalise_postcode(postcode_in):
    # We strip out the spaces - and reintroduce one four characters from end
    no_spaces = postcode_in.replace(' ', '')
    postcode = no_spaces[:len(no_spaces) - 3] + ' ' + no_spaces[-3:]
    return postcode


def _login_page(form=None, show_unauthorised_message=False, next_url=None):
    title_number = request.args.get('title_number')
    display_page_number = int(request.args.get('page') or 1)
    search_term = request.args.get('search_term', title_number)

    if not form:
        form = SigninForm(csrf_enabled=False)

    return render_template(
        'display_login.html',
        form=form,
        username=USERNAME,
        service_notice_html=app.config.get('SERVICE_NOTICE_HTML', None),
        unauthorised_title=None,
        unauthorised_description=None,
        next=next_url,
        title_number=title_number,
        search_term=search_term,
        page=display_page_number,
    )


def _title_details_page(title, search_term, breadcrumbs, show_pdf, full_title_data):
    return render_template(
        'display_title.html',
        title=title,
        username=USERNAME,
        search_term=search_term,
        breadcrumbs=breadcrumbs,
        show_pdf=show_pdf,
        full_title_data=full_title_data,
        is_caution_title=title_utils.is_caution_title(title),
    )


def _initial_search_page():
    return render_template(
        'search.html',
        form=TitleSearchForm(csrf_enabled=False),
        username=USERNAME,
    )


def _search_results_page(results, search_term):
    return render_template(
        'search_results.html',
        search_term=search_term,
        results=results,
        form=TitleSearchForm(csrf_enabled=False),
        username=USERNAME,
        breadcrumbs=[
            {'text': 'Search the land and property register', 'url': url_for('find_titles')},
            {'current': 'Search results'}
        ]
    )


def _create_string_date_only(datetoconvert):
    # converts to example : 12 August 2014
    date = datetoconvert.strftime('%-d %B %Y')
    return date


def _create_string_date_and_time(datetoconvert):
    # converts to example : 12 August 2014 12:34:06
    date = datetoconvert.strftime('%-d %B %Y at %H:%M:%S')
    return date


def _create_pdf_template(sub_registers, title, title_number):
    last_entry_date = _create_string_date_and_time(datetime(3001, 2, 3, 4, 5, 6))  # TODO use real date
    issued_date = _create_string_date_only(datetime.now())
    if title.get('edition_date'):
        edition_date = _create_string_date_only(datetime.strptime(title.get('edition_date'), "%Y-%m-%d"))
    else:
        edition_date = "No date given"
    return render_template('full_title.html', title_number=title_number, title=title,
                           last_entry_date=last_entry_date,
                           issued_date=issued_date,
                           edition_date=edition_date,
                           sub_registers=sub_registers)


@app.route('/titles/<title_number>/choose_summary_or_documents', methods=['GET'])
def choose_summary_or_documents(title_number):
    title = _get_register_title(title_number)

    if title:
        display_page_number = int(request.args.get('page') or 1)
        search_term = request.args.get('search_term', title_number)
        breadcrumbs = [
            {'text': 'Search the land and property register', 'url': url_for('find_titles')},
            {'text': 'Search results', 'url': url_for('find_titles_page', search_term=search_term, page=display_page_number)},
        ]

        return render_template(
            'choose_summary_or_documents.html',
            title=title,
            username=USERNAME,
            search_term=search_term,
            page=display_page_number,
            breadcrumbs=breadcrumbs,
            is_caution_title=title_utils.is_caution_title(title),
        )
    else:
        abort(404)


@app.route('/titles/<title_number>/chosen_summary_or_documents', methods=['POST'])
def chosen_summary_or_documents(title_number):
    display_page_number = int(request.args.get('page') or 1)
    search_term = request.args.get('search_term', title_number)

    products = request.form.getlist('summary_or_documents')
    session['products'] = products
    if 'documents' in products:
        return redirect(url_for('choose_documents', title_number=title_number, page=display_page_number, search_term=search_term))
    elif 'summary' in products:
        return redirect(url_for('choose_has_account', title_number=title_number, page=display_page_number, search_term=search_term))
    else:
        # TODO: use JavaScript to prevent users from submitting the form with no checkboxes selected
        abort(404)


@app.route('/titles/<title_number>/choose_documents', methods=['GET'])
def choose_documents(title_number):
    title = _get_register_title(title_number)

    if title:
        display_page_number = int(request.args.get('page') or 1)
        search_term = request.args.get('search_term', title_number)
        breadcrumbs = [
            {'text': 'Search the land and property register', 'url': url_for('find_titles')},
            {'text': 'Search results', 'url': url_for('find_titles_page', search_term=search_term, page=display_page_number)},
            {'text': 'Choose summary or documents', 'url': url_for('choose_summary_or_documents', title_number=title_number, search_term=search_term, page=display_page_number)},
        ]

        return render_template(
            'choose_documents.html',
            title=title,
            username=USERNAME,
            search_term=search_term,
            page=display_page_number,
            breadcrumbs=breadcrumbs,
        )
    else:
        abort(404)


@app.route('/titles/<title_number>/chosen_documents', methods=['POST'])
def chosen_documents(title_number):
    display_page_number = int(request.args.get('page') or 1)
    search_term = request.args.get('search_term', title_number)

    new_products = set(request.form.getlist('documents'))
    products = set(session['products'])
    products -= {'title_register', 'title_plan'}
    products |= new_products
    session['products'] = list(products)
    if 'title_register' in products or 'title_plan' in products:
        return redirect(url_for('choose_has_account', title_number=title_number, page=display_page_number, search_term=search_term))
    else:
        # TODO: use JavaScript to prevent users from submitting the form with no checkboxes selected
        abort(404)


@app.route('/sign_in', methods=['GET'])
def choose_has_account():
    title_number = request.args.get('title_number')
    display_page_number = int(request.args.get('page') or 1)
    search_term = request.args.get('search_term', title_number)

    return render_template(
        'choose_has_account.html',
        title_number=request.args.get('title_number'),
        username=USERNAME,
        search_term=request.args.get('search_term'),
        page=int(request.args.get('page') or 1),
    )


@app.route('/chosen_has_account', methods=['POST'])
def chosen_has_account():
    title_number = request.args.get('title_number')
    display_page_number = int(request.args.get('page') or 1)
    search_term = request.args.get('search_term', title_number)

    has_account = request.form.get('has_account') == 'yes'
    if has_account:
        return redirect(url_for('sign_in', title_number=title_number, page=display_page_number, search_term=search_term))
    else:
        return redirect(url_for('account_details', title_number=title_number, page=display_page_number, search_term=search_term))


@app.route('/account_details', methods=['GET', 'POST'])
def account_details():
    title_number = request.args.get('title_number')
    display_page_number = int(request.args.get('page') or 1)
    search_term = request.args.get('search_term', title_number)

    if request.method == 'GET':
        form = AccountForm(csrf_enabled=False)
        show_form = True
    else:  # POST
        form = AccountForm(request.form, csrf_enabled=False)
        show_form = not form.validate()

    if show_form:
        # no existing form (GET) or POSTed invalid form details
        return render_template(
            'account_details.html',
            form=form,
            title_number=title_number,
            username=USERNAME,
            search_term=search_term,
            page=display_page_number,
        )
    else:
        return redirect(url_for('account_created', title_number=title_number, page=display_page_number, search_term=search_term))


@app.route('/account_created', methods=['GET'])
def account_created():
    title_number = request.args.get('title_number')
    display_page_number = int(request.args.get('page') or 1)
    search_term = request.args.get('search_term', title_number)

    return render_template(
        'account_created.html',
        title_number=title_number,
        username=USERNAME,
        search_term=search_term,
        page=display_page_number,
    )


@app.route('/payment_details', methods=['GET', 'POST'])
def payment_details():
    title_number = request.args.get('title_number')
    title = _get_register_title(title_number)

    if title:
        display_page_number = int(request.args.get('page') or 1)
        search_term = request.args.get('search_term', title_number)

        if request.method == 'GET':
            form = PaymentForm(csrf_enabled=False)
            show_form = True
        else:  # POST
            form = PaymentForm(request.form, csrf_enabled=False)
            show_form = not form.validate()

        if show_form:
            product_keys = sorted(session['products'])
            product_info = {
                'summary': {'name': 'summary view', 'price': 1},
                'title_plan': {'name': 'title plan', 'price': 3},
                'title_register': {'name': 'title register', 'price': 3},
            }
            products = [product_info[product_key] for product_key in product_keys if product_key in product_info]
            total = sum([product['price'] for product in products])

            return render_template(
                'payment_details.html',
                title=title,
                form=form,
                username=USERNAME,
                search_term=search_term,
                page=display_page_number,
                products=products,
                total=total,
            )
        else:
            return redirect(url_for('get_title', title_number=title_number, page=display_page_number, search_term=search_term))
    else:
        abort(404)
