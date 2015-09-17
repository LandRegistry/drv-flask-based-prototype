from flask import Flask  # type: ignore

from service import error_handler, static, title_utils, template_filters

app = Flask(__name__)
app.debug = True
app.secret_key = 'blah'  # app.secret_key needed by flask.session

static.register_assets(app)

for filter_name, filter_method in template_filters.get_all_filters().items():
    app.jinja_env.filters[filter_name] = filter_method

error_handler.setup_errors(app)
