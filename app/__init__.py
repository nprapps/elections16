import app_config
import feedparser
import json

from . import utils
from gdoc import get_google_doc_html
from flask import Flask, jsonify, make_response, render_template
from models import models
from oauth.blueprint import oauth, oauth_required
from render_utils import make_context, make_gdoc_context, smarty_filter, urlencode_filter
from static.blueprint import static
from werkzeug.debug import DebuggedApplication


PODCAST_URL = 'http://npr.org/rss/podcast.php?id=510310'

app = Flask(__name__)
app.debug = app_config.DEBUG

app.add_template_filter(smarty_filter, name='smarty')
app.add_template_filter(urlencode_filter, name='urlencode')
app.add_template_filter(utils.comma_filter, name='comma')
app.add_template_filter(utils.percent_filter, name='percent')
app.add_template_filter(utils.normalize_percent_filter, name='normalize_percent')
app.add_template_filter(utils.ordinal_filter, name='ordinal')
app.add_template_filter(utils.ap_month_filter, name='ap_month')
app.add_template_filter(utils.ap_date_filter, name='ap_date')
app.add_template_filter(utils.ap_time_filter, name='ap_time')
app.add_template_filter(utils.ap_state_filter, name='ap_state')
app.add_template_filter(utils.ap_time_period_filter, name='ap_time_period')

PARTY_MAPPING = {
    'dem': {
       'AP': 'Dem',
       'long': 'Democrat',
    },
    'gop': {
        'AP': 'GOP',
        'long': 'Republican'
    }
}

@app.route('/preview/<path:path>/')
@oauth_required
def preview(path):
    context = make_context()
    path_parts = path.split('/')
    slug = path_parts[0]
    args = path_parts[1:]
    context['content'] = app.view_functions[slug](*args)
    return make_response(render_template('index.html', **context))


@app.route('/')
@oauth_required
def index():
    """
    Main published app view
    """
    context = make_context()

    state = context['state']
    script = context['COPY'][state]

    content = ''
    for row in script:
        function = row['function']
        params = ''
        if row['params']:
            params = row['params']

        if params:
            content += app.view_functions[function](params)
        else:
            content += app.view_functions[function]()

    context['content'] = content
    return make_response(render_template('index.html', **context))


@app.route('/card/<slug>/')
@oauth_required
def card(slug):
    """
    Render a generic card.
    """
    context = make_context()
    context['slug'] = slug
    context['template'] = 'basic-card'
    return render_template('cards/%s.html' % slug, **context)

@app.route('/podcast/')
@oauth_required
def podcast():
    """
    Render the podcast card
    """
    context = make_context()
    podcastdata = feedparser.parse(PODCAST_URL)
    latest = podcastdata.entries[0]
    context['podcast_title'] = latest.title
    context['podcast_link'] = latest.enclosures[0]['href']
    context['podcast_description'] = latest.description
    context['slug'] = 'podcast'
    context['template'] = 'podcast'

    return render_template('cards/podcast.html', **context)


@app.route('/results/<party>/')
@oauth_required
def results(party):
    """
    Render the results card
    """
    context = make_context()
    party_results = models.Result.select().where(
        models.Result.party == PARTY_MAPPING[party]['AP'],
        models.Result.level == 'state'
    )

    secondary_sort = sorted(list(party_results), key=utils.candidate_sort_lastname)
    sorted_results = sorted(secondary_sort, key=utils.candidate_sort_votecount, reverse=True)

    context['results'] = sorted_results
    context['slug'] = 'results-%s' % party
    context['template'] = 'results'
    context['route'] = '/results/%s/' % party

    if context['state'] != 'inactive':
        context['refresh_rate'] = 20

    return render_template('cards/results.html', **context)


@app.route('/get-caught-up/')
@oauth_required
def get_caught_up():
    context = make_context()

    key = app_config.CARD_GOOGLE_DOC_KEYS['get_caught_up']
    doc = get_google_doc_html(key)
    context.update(make_gdoc_context(doc))

    context['slug'] = 'get-caught-up'
    context['template'] = 'link-roundup'
    context['route'] = '/get-caught-up/'
    context['refresh_rate'] = 60

    return render_template('cards/link-roundup.html', **context)

@app.route('/what-happened/')
@oauth_required
def what_happened():
    context = make_context()

    key = app_config.CARD_GOOGLE_DOC_KEYS['what_happened']
    doc = get_google_doc_html(key)
    context.update(make_gdoc_context(doc))

    context['slug'] = 'what-happened'
    context['template'] = 'link-roundup'
    context['route'] = '/what-happened/'
    context['refresh_rate'] = 60

    return render_template('cards/link-roundup.html', **context)

@app.route('/title/')
@oauth_required
def title():
    context = make_context()

    key = app_config.CARD_GOOGLE_DOC_KEYS['title']
    doc = get_google_doc_html(key)
    context.update(make_gdoc_context(doc))

    context['slug'] = 'title'
    context['template'] = 'title'
    context['route'] = '/title/'
    context['refresh_rate'] = 60
    return render_template('cards/title.html', **context)


@app.route('/gdoc/<key>/')
@oauth_required
def gdoc(key):
    """
    Get a Google doc and parse for use in template.
    """
    context = make_context()
    context['content'] = get_google_doc_html(key)
    return render_template('cards/gdoc.html', **context)


@app.route('/current-state.json')
@oauth_required
def current_state():
    context = make_context()

    data = {
        'state': context['state']
    }

    return jsonify(**data)

def never_cache_preview(response):
    """
    Ensure preview is never cached
    """
    response.cache_control.max_age = 0
    response.cache_control.no_cache = True
    response.cache_control.must_revalidate = True
    response.cache_control.no_store = True
    return response

app.register_blueprint(static)
app.register_blueprint(oauth)

# Enable Werkzeug debug pages
if app_config.DEBUG:
    app.after_request(never_cache_preview)
    wsgi_app = DebuggedApplication(app, evalex=False)
else:
    wsgi_app = app
