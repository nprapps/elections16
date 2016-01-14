import app_config
import feedparser

from flask import Flask, make_response, render_template
from models import models
from oauth.blueprint import oauth, oauth_required
from render_utils import make_context, smarty_filter, urlencode_filter
from static.blueprint import static
from werkzeug.debug import DebuggedApplication


PODCAST_URL = 'http://npr.org/rss/podcast.php?id=510310'

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
    #import ipdb; ipdb.set_trace();
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

    state = context['COPY']['meta']['state']['value']
    script = context['COPY'][state]

    content = ''
    for row in script:
        function = row['function']
        params = ''
        if row['params']:
            params = row['params']

        if params:
            content += app.view_functions[function](params).data
        else:
            content += app.view_functions[function]().data

    context['content'] = content
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


@app.route('/podcast/')
@oauth_required
def podcast():
    context = make_context()
    podcastdata = feedparser.parse(PODCAST_URL)
    latest = podcastdata.entries[0]
    context['podcast_title'] = latest.title
    context['podcast_link'] = latest.enclosures[0]['href']
    context['podcast_description'] = latest.description
    return make_response(render_template('cards/podcast.html', **context))



app.register_blueprint(static)
app.register_blueprint(oauth)

# Enable Werkzeug debug pages
if app_config.DEBUG:
    wsgi_app = DebuggedApplication(app, evalex=False)
else:
    wsgi_app = app
