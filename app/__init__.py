import app_config

from gdoc import get_google_doc, DocParser
from flask import Flask, make_response, render_template
from models import models
from oauth.blueprint import oauth, oauth_required
from render_utils import make_context, smarty_filter, urlencode_filter
from static.blueprint import static
from werkzeug.debug import DebuggedApplication

app = Flask(__name__)
app.debug = app_config.DEBUG

app.add_template_filter(smarty_filter, name='smarty')
app.add_template_filter(urlencode_filter, name='urlencode')


@app.route('/preview/<path:path>/')
@oauth_required
def preview(path):
    context = make_context()
    path_parts = path.split('/')
    slug = path_parts[0]
    args = path_parts[1:]
    context['content'] = app.view_functions[slug](*args).data
    return make_response(render_template('index.html', **context))


@app.route('/')
@oauth_required
def index():
    """
    Main published app view
    """
    context = make_context()
    context['results'] = models.Result.select()
    return make_response(render_template('index.html', **context))


@app.route('/card/<slug>/')
@oauth_required
def card(slug):
    """
    Stubby "hello world" view
    """
    context = make_context()
    context['slug'] = slug
    return make_response(render_template('cards/%s.html' % slug, **context))


@app.route('/gdoc/<key>/')
@oauth_required
def gdoc(key):
    """
    Get a Google doc and parse for use in template.
    """
    context = make_context()
    html_string = get_google_doc(key)
    context['content'] = DocParser(html_string)
    return make_response(render_template('cards/gdoc.html', **context))


app.register_blueprint(static)
app.register_blueprint(oauth)

# Enable Werkzeug debug pages
if app_config.DEBUG:
    wsgi_app = DebuggedApplication(app, evalex=False)
else:
    wsgi_app = app
