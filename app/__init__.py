import app_config
import simplejson as json

from . import utils
from collections import OrderedDict
from datetime import date, datetime
from gdoc import get_google_doc_html
from flask import Flask, jsonify, make_response, render_template
from models import models
from oauth.blueprint import oauth, oauth_required
from peewee import fn
from playhouse.shortcuts import model_to_dict
from render_utils import make_context, make_gdoc_context, smarty_filter, urlencode_filter
from static.blueprint import static
from werkzeug.debug import DebuggedApplication

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
       'class': 'democrat',
       'adverb': 'Democratic',
    },
    'gop': {
        'AP': 'GOP',
        'long': 'Republican',
        'class': 'republican',
        'adverb': 'Republican',
    }
}


DELEGATE_WHITELIST = {
    'gop': [
        'Bush',
        'Carson',
        'Christie',
        'Cruz',
        'Fiorina',
        'Gilmore',
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


class APDatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            thedate = utils.ap_date_filter(obj.strftime('%m/%d/%Y'))
            thetime = utils.ap_time_filter(obj.strftime('%I:%M'))
            theperiod = utils.ap_time_period_filter(obj.strftime('%p'))
            return '{0}, {1} {2}'.format(thedate, thetime, theperiod)
        elif isinstance(obj, date):
            return obj.isoformat()
        else:
            return super(APDatetimeEncoder, self).default(obj)


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

    key = app_config.CARD_GOOGLE_DOC_KEYS['podcast']
    doc = get_google_doc_html(key)
    context.update(make_gdoc_context(doc))

    context['slug'] = 'podcast'
    context['template'] = 'podcast'

    return render_template('cards/podcast.html', **context)

@app.route('/audio-story/<key>')
@oauth_required
def audio_story(key):
    """
    Render the podcast card
    """
    context = make_context()

    doc = get_google_doc_html(key)
    context.update(make_gdoc_context(doc))

    context['slug'] = 'audio-story-%s' % key
    context['template'] = 'audio-story'

    return render_template('cards/audio-story.html', **context)


@app.route('/results/<party>/')
@oauth_required
def results(party):
    """
    Render the results card
    """

    context = make_context()

    results, other_votecount, other_votepct, last_updated = get_results(party, app_config.NEXT_ELECTION_DATE)

    context['results'] = results
    context['other_votecount'] = other_votecount
    context['other_votepct'] = other_votepct
    context['last_updated'] = last_updated
    context['slug'] = 'results-%s' % party
    context['template'] = 'results'
    context['route'] = '/results/%s/' % party

    if context['state'] != 'inactive':
        context['refresh_rate'] = 20

    return render_template('cards/results.html', **context)


@app.route('/delegates/<party>/')
@oauth_required
def delegates(party):
    """
    Render the results card
    """

    context = make_context()

    ap_party = PARTY_MAPPING[party]['AP']

    candidates = models.CandidateDelegates.select().where(
        models.CandidateDelegates.party == ap_party,
        models.CandidateDelegates.level == 'nation',
        models.CandidateDelegates.last << DELEGATE_WHITELIST[party]
    ).order_by(
        -models.CandidateDelegates.delegates_count,
        models.CandidateDelegates.last
    )

    context['last_updated'] = datetime.utcnow()

    context['candidates'] = candidates
    context['needed'] = app_config.DELEGATE_ESTIMATES[ap_party]
    context['party'] = ap_party

    context['party_class'] = PARTY_MAPPING[party]['class']
    context['party_long'] = PARTY_MAPPING[party]['adverb']

    context['slug'] = 'delegates-%s' % party
    context['template'] = 'delegates'
    context['route'] = '/delegates/%s/' % party

    if context['state'] != 'inactive':
        context['refresh_rate'] = 60

    return render_template('cards/delegates.html', **context)


@app.route('/live-audio/')
@oauth_required
def live_audio():
    context = make_context()

    live_audio_state = context['COPY']['meta']['live_audio']['value']

    if live_audio_state == 'live':
        key = app_config.CARD_GOOGLE_DOC_KEYS['live_coverage_active']
        context['live'] = True
    else:
        key = app_config.CARD_GOOGLE_DOC_KEYS['live_coverage_inactive']
        context['live'] = False

    doc = get_google_doc_html(key)
    context.update(make_gdoc_context(doc))

    context['slug'] = 'live-audio'
    context['template'] = 'live-audio'
    context['route'] = '/live-audio/'
    context['refresh_rate'] = 60

    return render_template('cards/live-audio.html', **context)


@app.route('/data/results-<electiondate>.json')
def results_json(electiondate):
    data = {
        'gop': None,
        'dem': None,
    }

    for party in data.keys():
        results, other_votecount, other_votepct, lastupdated = get_results(party, electiondate)
        data[party] = {
            'results': results,
            'other_votecount': other_votecount,
            'other_votepct': other_votepct,
            'lastupdated': lastupdated
        }

    return json.dumps(data, use_decimal=True, cls=APDatetimeEncoder)


@app.route('/data/delegates.json')
def delegates_json():
    whitelist = DELEGATE_WHITELIST['gop'] + DELEGATE_WHITELIST['dem']
    data = OrderedDict()

    data['nation'] = OrderedDict((('dem', []), ('gop', [])))
    for party in ['dem', 'gop']:
        national_candidates = models.CandidateDelegates.select().where(
            models.CandidateDelegates.party == PARTY_MAPPING[party]['AP'],
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
                models.CandidateDelegates.party == PARTY_MAPPING[party]['AP'],
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

    return json.dumps(data, use_decimal=True, cls=APDatetimeEncoder)


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

@app.route('/whats-happening/')
@oauth_required
def whats_happening():
    context = make_context()

    key = app_config.CARD_GOOGLE_DOC_KEYS['whats_happening']
    doc = get_google_doc_html(key)
    context.update(make_gdoc_context(doc))

    context['slug'] = 'whats-happening'
    context['template'] = 'link-roundup'
    context['route'] = '/whats-happening/'
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


def get_results(party, electiondate):
    """
    Results getter
    """
    ap_party = PARTY_MAPPING[party]['AP']
    party_results = models.Result.select().where(
        models.Result.electiondate == electiondate,
        models.Result.party == ap_party,
        models.Result.level == 'state'
    )

    filtered, other_votecount, other_votepct = utils.collate_other_candidates(list(party_results), ap_party)

    secondary_sort = sorted(filtered, key=utils.candidate_sort_lastname)
    sorted_results = sorted(secondary_sort, key=utils.candidate_sort_votecount, reverse=True)

    serialized_results = []
    for result in sorted_results:
        serialized_results.append(model_to_dict(result, backrefs=True))

    latest_result = models.Result.select(
        fn.Max(models.Result.lastupdated).alias('lastupdated')
    ).where(
        models.Result.party == PARTY_MAPPING[party]['AP'],
        models.Result.level == 'state'
    ).get()

    return serialized_results, other_votecount, other_votepct, latest_result.lastupdated


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
