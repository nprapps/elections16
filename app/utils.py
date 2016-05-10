from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal, ROUND_DOWN
from models import models
from peewee import fn
from playhouse.shortcuts import model_to_dict
from pytz import timezone
from time import time

import app_config
import copytext
import simplejson as json
import xlrd

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
AP_MONTHS = ['Jan.', 'Feb.', 'March', 'April', 'May', 'June', 'July', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.']
ORDINAL_SUFFIXES = { 1: 'st', 2: 'nd', 3: 'rd' }

USPS_TO_AP_STATE = {
    'AL': 'Ala.',
    'AK': 'Alaska',
    'AR': 'Ark.',
    'AZ': 'Ariz.',
    'CA': 'Calif.',
    'CO': 'Colo.',
    'CT': 'Conn.',
    'DC': 'D.C.',
    'DE': 'Del.',
    'FL': 'Fla.',
    'GA': 'Ga.',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Ill.',
    'IN': 'Ind.',
    'KS': 'Kan.',
    'KY': 'Ky.',
    'LA': 'La.',
    'MA': 'Mass.',
    'MD': 'Md.',
    'ME': 'Maine',
    'MI': 'Mich.',
    'MN': 'Minn.',
    'MO': 'Mo.',
    'MS': 'Miss.',
    'MT': 'Mont.',
    'NC': 'N.C.',
    'ND': 'N.D.',
    'NE': 'Neb.',
    'NH': 'N.H.',
    'NJ': 'N.J.',
    'NM': 'N.M.',
    'NV': 'Nev.',
    'NY': 'N.Y.',
    'OH': 'Ohio',
    'OK': 'Okla.',
    'OR': 'Ore.',
    'PA': 'Pa.',
    'PR': 'P.R.',
    'RI': 'R.I.',
    'SC': 'S.C.',
    'SD': 'S.D.',
    'TN': 'Tenn.',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Va.',
    'VT': 'Vt.',
    'WA': 'Wash.',
    'WI': 'Wis.',
    'WV': 'W.Va.',
    'WY': 'Wyo.'
}

GOP_CANDIDATES = [
    'Ted Cruz',
    'John Kasich',
    'Donald Trump'
]

DEM_CANDIDATES = [
    'Hillary Clinton',
    'Bernie Sanders'
]

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


def comma_filter(value):
    """
    Format a number with commas.
    """
    return '{:,}'.format(value)


def percent_filter(value):
    """
    Format percentage
    """
    value = Decimal(value) * Decimal(100)
    if value == 0:
        return '0%'
    elif value == 100:
        return '100%'
    elif value > 0 and value < 1:
        return '<1%'
    else:
        cleaned_pct = value.quantize(Decimal('.1'), rounding=ROUND_DOWN)
        return '{:.1f}%'.format(cleaned_pct)


def ordinal_filter(num):
    """
    Format a number as an ordinal.
    """
    num = int(num)

    if 10 <= num % 100 <= 20:
        suffix = 'th'
    else:
        suffix = ORDINAL_SUFFIXES.get(num % 10, 'th')

    return unicode(num) + suffix


def ap_month_filter(month):
    """
    Convert a month name into AP abbreviated style.
    """
    return AP_MONTHS[int(month) - 1]


def ap_date_filter(value):
    """
    Converts a date string in m/d/yyyy format into AP style.
    """
    if isinstance(value, basestring):
        value = datetime.strptime(value, '%m/%d/%Y')
    value_tz = _set_timezone(value)
    output = AP_MONTHS[value_tz.month - 1]
    output += ' ' + unicode(value_tz.day)
    output += ', ' + unicode(value_tz.year)

    return output


def ap_time_filter(value):
    """
    Converts a datetime or string in hh:mm format into AP style.
    """
    if isinstance(value, basestring):
        value = datetime.strptime(value, '%I:%M')
    value_tz = _set_timezone(value)
    value_year = value_tz.replace(year=2016)
    return value_year.strftime('%-I:%M')


def ap_state_filter(usps):
    """
    Convert a USPS state abbreviation into AP style.
    """
    return USPS_TO_AP_STATE[unicode(usps)]


def ap_time_period_filter(value):
    """
    Converts Python's AM/PM into AP Style's a.m./p.m.
    """
    if isinstance(value, basestring):
        value = datetime.strptime(value, '%p')
    value_tz = _set_timezone(value)
    value_year = value_tz.replace(year=2016)
    periods = '.'.join(value_year.strftime('%p')) + '.'
    return periods.lower()


def candidate_sort_lastname(item):
    if item.winner:
        return -1
    elif item.last == 'Other' or item.last == 'Uncommitted' or item.last == 'Write-ins':
        return 'zzz'
    else:
        return item.last


def candidate_sort_votecount(item):
    return item.votecount


def _set_timezone(value):
    datetime_obj_utc = value.replace(tzinfo=timezone('GMT'))
    datetime_obj_est = datetime_obj_utc.astimezone(timezone('US/Eastern'))
    return datetime_obj_est


def collate_other_candidates(results, party):
    if party == 'GOP':
        whitelisted_candidates = GOP_CANDIDATES
    elif party == 'Dem':
        whitelisted_candidates = DEM_CANDIDATES

    other_votecount = 0
    other_votepct = 0

    for result in reversed(results):
        candidate_name = '%s %s' % (result.first, result.last)
        if candidate_name not in whitelisted_candidates:
            other_votecount += result.votecount
            other_votepct += result.votepct
            results.remove(result)

    return results, other_votecount, other_votepct


def set_delegates_updated_time():
    """
    Write timestamp to filesystem
    """
    now = time()
    with open(app_config.DELEGATE_TIMESTAMP_FILE, 'w') as f:
        f.write(str(now))


def get_delegates_updated_time():
    """
    Read timestamp from file system and return UTC datetime object.
    """
    with open(app_config.DELEGATE_TIMESTAMP_FILE) as f:
        updated_ts = f.read()

    return datetime.utcfromtimestamp(float(updated_ts))


def never_cache_preview(response):
    """
    Ensure preview is never cached
    """
    response.cache_control.max_age = 0
    response.cache_control.no_cache = True
    response.cache_control.must_revalidate = True
    response.cache_control.no_store = True
    return response


def open_db():
    """
    Open db connection
    """
    models.db.connect()


def close_db(response):
    """
    Close db connection
    """
    models.db.close()
    return response


def get_results(party, electiondate):
    ap_party = PARTY_MAPPING[party]['AP']
    race_ids = models.Result.select(fn.Distinct(models.Result.raceid), models.Result.statename).where(
        models.Result.electiondate == electiondate,
        models.Result.party == ap_party,
        models.Result.level == 'state',
        models.Result.officename == 'President',
    )

    blacklist = app_config.RACE_BLACKLIST.get(electiondate)
    if blacklist:
        race_ids = race_ids.where(~(models.Result.raceid << blacklist))

    race_ids.order_by(models.Result.statename, models.Result.raceid)

    # Get copy once
    copy_obj = copytext.Copy(app_config.COPY_PATH)
    copy = copy_obj['meta']._serialize()

    output = []
    for race in race_ids:
        output.append(get_race_results(race.raceid, ap_party, copy))

    return output


def get_race_results(raceid, party, copy):
    """
    Results getter
    """
    race_results = models.Result.select().where(
        models.Result.raceid == raceid,
        models.Result.level == 'state'
    )

    filtered, other_votecount, other_votepct = collate_other_candidates(list(race_results), party)

    secondary_sort = sorted(filtered, key=candidate_sort_lastname)
    sorted_results = sorted(secondary_sort, key=candidate_sort_votecount, reverse=True)

    called = False

    serialized_results = []
    for result in sorted_results:
        if (result.winner and result.call[0].accept_ap) or result.call[0].override_winner:
            called = True
        serialized_results.append(model_to_dict(result, backrefs=True))

    output = {
        'results': serialized_results,
        'other_votecount': other_votecount,
        'other_votepct': other_votepct,
        'statename': serialized_results[0]['statename'],
        'statepostal': serialized_results[0]['statepostal'],
        'precinctsreportingpct': serialized_results[0]['precinctsreportingpct'],
        'precinctsreporting': serialized_results[0]['precinctsreporting'],
        'precinctstotal': serialized_results[0]['precinctstotal'],
        'total': tally_results(raceid),
        'called': called,
        'race_type': '',
        'note': get_race_note(serialized_results[0], copy)
    }

    if len(serialized_results[0]['meta']):
        output.update({
            'poll_closing': serialized_results[0]['meta'][0].get('poll_closing'),
            'race_type': serialized_results[0]['meta'][0].get('race_type'),
            'order': serialized_results[0]['meta'][0].get('order')
        })

    return output


def get_race_note(race, copy):
    """
    Pluck race note out of meta sheet
    """
    key = '{0}_{1}_note'.format(race['statepostal'], race['party']).lower()
    return copy.get(key, '')


def group_poll_closings(races):
    poll_closing_orders = []
    for race in races:
        if race['order'] not in poll_closing_orders:
            poll_closing_orders.append(race['order'])

    poll_closing_orders.sort()

    grouped = OrderedDict()
    for group in poll_closing_orders:
        grouped[group] = {
            'poll_closing': '',
            'races': []
        }

        for race in races:
            if race['precinctsreporting'] == 0 and not race['called'] and race['order'] == group:
                grouped[group]['poll_closing'] = race['poll_closing']
                grouped[group]['races'].append(race['statename'])

    return grouped


def get_unreported_races(races):
    unreported = [race['statename'] for race in races if race['precinctsreporting'] == 0 and not race['called']]
    return unreported


def _format_poll_closing(poll_closing):
    formatted_time = ap_time_filter(poll_closing)
    formatted_period = ap_time_period_filter(poll_closing)
    return '{0} {1}'.format(formatted_time, formatted_period)


def get_last_updated(races):
    last_updated = None

    for race in races:
        if race['called'] or race['precinctsreporting'] > 0:
            for result in race['results']:
                if not last_updated or result['lastupdated'] > last_updated:
                    last_updated = result['lastupdated']

    if not last_updated:
        last_updated = datetime.utcnow()

    return last_updated


def tally_results(raceid):
    """
    Add results for a given party on a given date.
    """
    tally = models.Result.select(fn.SUM(models.Result.votecount)).where(
        models.Result.level == 'state',
        models.Result.raceid == raceid
    ).scalar()
    return tally


def convert_serial_date(value):
    parsed = datetime(*(xlrd.xldate_as_tuple(float(value), 0)))
    eastern = timezone('US/Eastern')
    parsed_eastern = eastern.localize(parsed)
    parsed_utc = parsed_eastern.astimezone(timezone('GMT'))
    parsed_naive = parsed_utc.replace(tzinfo=None)
    return parsed_naive


class APDatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            thedate = ap_date_filter(obj)
            thetime = ap_time_filter(obj)
            theperiod = ap_time_period_filter(obj)
            return '{0}, {1} {2}'.format(thedate, thetime, theperiod)
        elif isinstance(obj, date):
            return obj.isoformat()
        else:
            return super(APDatetimeEncoder, self).default(obj)
