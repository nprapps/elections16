from decimal import Decimal

import operator
import re

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
    if not value:
        return ''

    bits = unicode(value).split('/')

    month, day, year = bits

    output = AP_MONTHS[int(month) - 1]
    output += ' ' + unicode(int(day))
    output += ', ' + year

    return output

def ap_state_filter(usps):
    """
    Convert a USPS state abbreviation into AP style.
    """
    return USPS_TO_AP_STATE[unicode(usps)]

def ap_time_period_filter(value):
    """
    Converts Python's AM/PM into AP Style's a.m./p.m.
    """
    if not value:
        return ''

    periods = '.'.join(value.lower()) + '.'

    return periods


def candidate_sort_lastname(item):
    if item.last == 'Other' or item.last == 'Uncommitted' or item.last == 'Write-ins':
        return 'zzz'
    else:
        return item.last


def candidate_sort_votecount(item):
    return item.votecount
