from flask import Flask  # type: ignore

from service import static, title_utils, template_filters

app = Flask(__name__)
app.debug = True

static.register_assets(app)

for filter_name, filter_method in template_filters.get_all_filters().items():
    app.jinja_env.filters[filter_name] = filter_method
