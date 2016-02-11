from datetime import datetime
from decimal import Decimal
from models import models
from playhouse.shortcuts import model_to_dict
from pytz import timezone
from time import time

import app_config
import simplejson as json

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
    'Jeb Bush',
    'Ben Carson',
    'Chris Christie',
    'Ted Cruz',
    'Carly Fiorina',
    'Jim Gilmore',
    'John Kasich',
    'Marco Rubio',
    'Donald Trump'
]

DEM_CANDIDATES = [
    'Hillary Clinton',
    'Bernie Sanders'
]

def comma_filter(value):
    """
    Format a number with commas.
    """
    return '{:,}'.format(value)

def percent_filter(value):
    """
    Format percentage
    """
    one_decimal = '{:.1f}%'.format(value)
    return one_decimal

def normalize_percent_filter(value):
    """
    Multiply value times 100
    """
    return Decimal(value) * Decimal(100)

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
    i = MONTHS.index(month)

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
    Converts a time string in hh:mm format into AP style.
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
    if item.last == 'Other' or item.last == 'Uncommitted' or item.last == 'Write-ins':
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

    filtered, other_votecount, other_votepct = collate_other_candidates(list(party_results), ap_party)

    secondary_sort = sorted(filtered, key=candidate_sort_lastname)
    sorted_results = sorted(secondary_sort, key=candidate_sort_votecount, reverse=True)

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
