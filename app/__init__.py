import app_config
import m3u8
import os
import simplejson as json
import sys

from . import utils
from collections import OrderedDict
from flask import Flask, jsonify, make_response, render_template
from itertools import groupby
from models import models
from oauth.blueprint import oauth, oauth_required, get_document
from peewee import fn
from playhouse.shortcuts import model_to_dict
from render_utils import make_context, make_gdoc_context, make_newsletter_context, smarty_filter, urlencode_filter
from static.blueprint import static
from werkzeug.debug import DebuggedApplication

app = Flask(__name__)
app.debug = app_config.DEBUG

app.add_template_filter(smarty_filter, name='smarty')
app.add_template_filter(urlencode_filter, name='urlencode')
app.add_template_filter(utils.comma_filter, name='comma')
app.add_template_filter(utils.percent_filter, name='percent')
app.add_template_filter(utils.ordinal_filter, name='ordinal')
app.add_template_filter(utils.ap_month_filter, name='ap_month')
app.add_template_filter(utils.ap_date_filter, name='ap_date')
app.add_template_filter(utils.ap_time_filter, name='ap_time')
app.add_template_filter(utils.ap_state_filter, name='ap_state')
app.add_template_filter(utils.ap_time_period_filter, name='ap_time_period')

DELEGATE_WHITELIST = {
    'gop': [
        'Bush',
        'Carson',
        'Christie',
        'Cruz',
        'Fiorina',
        'Gilmore',
        'Huckabee',
        'Kasich',
        'Paul',
        'Rubio',
        'Trump',
    ],
    'dem': [
        'Clinton',
        'Sanders',
    ],
}

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'

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

    context.update(make_gdoc_context('podcast'))

    context['slug'] = 'podcast'
    context['template'] = 'podcast'

    return render_template('cards/podcast.html', **context)

@app.route('/results-single/<party>/')
@oauth_required
def results_single(party):
    context = make_context()

    races = utils.get_results(party, app_config.NEXT_ELECTION_DATE)
    last_updated = utils.get_last_updated(races)

    context['races'] = races
    context['last_updated'] = last_updated
    context['party'] = utils.PARTY_MAPPING[party]['adverb']
    context['slug'] = 'results-%s' % party
    context['template'] = 'results'
    context['route'] = '/results-single/%s/' % party

    context['refresh_rate'] = app_config.LOAD_RESULTS_INTERVAL

    return render_template('cards/results.html', **context)

@app.route('/results/<party>/')
@oauth_required
def results(party):
    """
    Render the results card
    """

    context = make_context()

    races = utils.get_results(party, app_config.NEXT_ELECTION_DATE)
    poll_closings = utils.group_poll_closings(races)
    unreported_races = utils.get_unreported_races(races)
    last_updated = utils.get_last_updated(races)

    context['races'] = races
    context['poll_closings'] = poll_closings
    context['unreported_races'] = unreported_races
    context['last_updated'] = last_updated
    context['party'] = utils.PARTY_MAPPING[party]['adverb']
    context['slug'] = 'results-%s' % party
    context['template'] = 'results-multi'
    context['route'] = '/results/%s/' % party

    context['refresh_rate'] = app_config.LOAD_RESULTS_INTERVAL

    return render_template('cards/results-multi.html', **context)


@app.route('/delegates/<party>/')
@oauth_required
def delegates(party):
    """
    Render the results card
    """

    context = make_context()

    ap_party = utils.PARTY_MAPPING[party]['AP']

    candidates = models.CandidateDelegates.select().where(
        models.CandidateDelegates.party == ap_party,
        models.CandidateDelegates.level == 'nation',
        models.CandidateDelegates.last << DELEGATE_WHITELIST[party],
        models.CandidateDelegates.delegates_count > 0
    ).order_by(
        -models.CandidateDelegates.delegates_count,
        models.CandidateDelegates.last
    )

    context['last_updated'] = utils.get_delegates_updated_time()

    context['candidates'] = candidates
    context['needed'] = list(candidates)[0].party_need
    context['party'] = ap_party

    context['party_class'] = utils.PARTY_MAPPING[party]['class']
    context['party_long'] = utils.PARTY_MAPPING[party]['adverb']

    context['slug'] = 'delegates-%s' % party
    context['template'] = 'delegates'
    context['route'] = '/delegates/%s/' % party

    context['refresh_rate'] = app_config.LOAD_DELEGATES_INTERVAL

    return render_template('cards/delegates.html', **context)


@app.route('/live-audio/')
@oauth_required
def live_audio():
    context = make_context()

    live_audio_state = context['COPY']['meta']['live_audio']['value']
    context.update(make_gdoc_context('live_audio'))

    pointer = m3u8.load(app_config.LIVESTREAM_POINTER_FILE)
    context['live_audio_url'] = pointer.segments[0].uri

    if live_audio_state == 'live':
        context['live'] = True
    else:
        context['live'] = False

    context['slug'] = 'live-audio'
    context['template'] = 'live-audio'
    context['route'] = '/live-audio/'
    context['refresh_rate'] = app_config.LOAD_DOCS_INTERVAL

    return render_template('cards/live-audio.html', **context)


@app.route('/newsletter-roundup/')
@oauth_required
def newsletter_roundup():
    context = make_context()
    context.update(make_newsletter_context())
    context['slug'] = 'newsletter-roundup'
    context['template'] = 'newsletter-roundup'
    context['route'] = '/newsletter-roundup/'
    context['refresh_rate'] = 30

    return render_template('cards/newsletter-roundup.html', **context)


@app.route('/data/results-<electiondate>.json')
def results_json(electiondate):
    data = {
        'gop': None,
        'dem': None,
    }

    for party in data.keys():
        results = utils.get_results(party, electiondate)

        # Hack! Simply set last updated on every record to avoid breaking
        # live updating widget. @TODO chat with Aly about re-shaping the data
        # a bit.
        lastupdated = utils.get_last_updated(results)
        for race in results:
            for race_result in race['results']:
                race_result['lastupdated'] = lastupdated

        grouped_results = [(k, list(g)) for k, g in groupby(results, lambda x: x['statepostal'])]
        data[party] = OrderedDict(grouped_results)

    return json.dumps(data, use_decimal=True, cls=utils.APDatetimeEncoder)


@app.route('/data/delegates.json')
def delegates_json():
    whitelist = DELEGATE_WHITELIST['gop'] + DELEGATE_WHITELIST['dem']
    data = OrderedDict()

    data['nation'] = OrderedDict((('dem', []), ('gop', [])))
    for party in ['dem', 'gop']:
        national_candidates = models.CandidateDelegates.select().where(
            models.CandidateDelegates.party == utils.PARTY_MAPPING[party]['AP'],
            models.CandidateDelegates.level == 'nation',
            models.CandidateDelegates.last << whitelist
        ).order_by(
            -models.CandidateDelegates.delegates_count,
            models.CandidateDelegates.last
        )

        data['nation'][party] = []
        for result in national_candidates:
            data['nation'][party].append(model_to_dict(result))

    states = models.CandidateDelegates \
                .select(fn.Distinct(models.CandidateDelegates.state)) \
                .order_by(models.CandidateDelegates.state)

    for state_obj in states:
        data[state_obj.state] = OrderedDict()

        for party in ['dem', 'gop']:
            state_candidates = models.CandidateDelegates.select().where(
                models.CandidateDelegates.party == utils.PARTY_MAPPING[party]['AP'],
                models.CandidateDelegates.state == state_obj.state,
                models.CandidateDelegates.level == 'state',
                models.CandidateDelegates.last << whitelist
            ).order_by(
                -models.CandidateDelegates.delegates_count,
                models.CandidateDelegates.last
            )

            data[state_obj.state][party] = []
            for result in state_candidates:
                data[state_obj.state][party].append(model_to_dict(result))

    data['last_updated'] = utils.get_delegates_updated_time()
    return json.dumps(data, use_decimal=True, cls=utils.APDatetimeEncoder)


@app.route('/get-caught-up/')
@oauth_required
def get_caught_up():
    context = make_context()

    context.update(make_gdoc_context('get_caught_up'))

    context['slug'] = 'get-caught-up'
    context['template'] = 'link-roundup'
    context['route'] = '/get-caught-up/'
    context['refresh_rate'] = app_config.LOAD_DOCS_INTERVAL

    return render_template('cards/link-roundup.html', **context)

@app.route('/whats-happening/')
@oauth_required
def whats_happening():
    context = make_context()

    context.update(make_gdoc_context('whats_happening'))

    context['slug'] = 'whats-happening'
    context['template'] = 'link-roundup'
    context['route'] = '/whats-happening/'
    context['refresh_rate'] = app_config.LOAD_DOCS_INTERVAL

    return render_template('cards/link-roundup.html', **context)

@app.route('/what-happened/')
@oauth_required
def what_happened():
    context = make_context()

    context.update(make_gdoc_context('what_happened'))

    context['slug'] = 'what-happened'
    context['template'] = 'link-roundup'
    context['route'] = '/what-happened/'
    context['refresh_rate'] = app_config.LOAD_DOCS_INTERVAL

    return render_template('cards/link-roundup.html', **context)

@app.route('/title/')
@oauth_required
def title():
    context = make_context()

    context.update(make_gdoc_context('title'))

    context['slug'] = 'title'
    context['template'] = 'title'
    context['route'] = '/title/'
    context['refresh_rate'] = app_config.LOAD_DOCS_INTERVAL
    return render_template('cards/title.html', **context)


@app.route('/gdoc/<key>/')
@oauth_required
def gdoc(key):
    """
    Get a Google doc and parse for use in template.
    """
    context = make_context()
    file_path = 'data/%s.html' % key
    get_document(key, file_path)
    context.update(make_gdoc_context(key))
    os.remove(file_path)
    return render_template('cards/gdoc.html', **context)


@app.route('/current-state.json')
@oauth_required
def current_state():
    context = make_context()

    data = {
        'state': context['state']
    }

    return jsonify(**data)


app.register_blueprint(static)
app.register_blueprint(oauth)

app.before_request(utils.open_db)
app.after_request(utils.close_db)

# Enable Werkzeug debug pages
if app_config.DEBUG:
    app.after_request(utils.never_cache_preview)
    wsgi_app = DebuggedApplication(app, evalex=False)
else:
    wsgi_app = app
