#!/usr/bin/env python

"""
Project-wide application configuration.

DO NOT STORE SECRETS, PASSWORDS, ETC. IN THIS FILE.
They will be exposed to users. Use environment variables instead.
See get_secrets() below for a fast way to access them.
"""

import logging
import os

from authomatic.providers import oauth2
from authomatic import Authomatic


"""
NAMES
"""
# Project name to be used in urls
# Use dashes, not underscores!
PROJECT_SLUG = 'elections16'

# Project name to be used in file paths
PROJECT_FILENAME = 'elections16'

# The name of the repository containing the source
REPOSITORY_NAME = 'elections16'
GITHUB_USERNAME = 'nprapps'
REPOSITORY_URL = 'git@github.com:%s/%s.git' % (GITHUB_USERNAME, REPOSITORY_NAME)
REPOSITORY_ALT_URL = None # 'git@bitbucket.org:nprapps/%s.git' % REPOSITORY_NAME'

# Project name used for assets rig
# Should stay the same, even if PROJECT_SLUG changes
ASSETS_SLUG = 'elections16'

"""
DEPLOYMENT
"""
PRODUCTION_S3_BUCKET = 'elections.npr.org'

ASSETS_S3_BUCKET = 'assets.apps.npr.org'

ARCHIVE_S3_BUCKET = 'election-backup.apps.npr.org'

DEFAULT_MAX_AGE = 60

RELOAD_TRIGGER = True
RELOAD_CHECK_INTERVAL = 60

PRODUCTION_SERVERS = ['54.189.43.202']
STAGING_SERVERS = ['54.212.140.247']


# Should code be deployed to the web/cron servers?
DEPLOY_TO_SERVERS = True

SERVER_USER = 'ubuntu'
SERVER_PYTHON = 'python2.7'
SERVER_PROJECT_PATH = '/home/%s/apps/%s' % (SERVER_USER, PROJECT_FILENAME)
SERVER_REPOSITORY_PATH = '%s/repository' % SERVER_PROJECT_PATH
SERVER_VIRTUALENV_PATH = '%s/virtualenv' % SERVER_PROJECT_PATH

# Should the crontab file be installed on the servers?
# If True, DEPLOY_TO_SERVERS must also be True
DEPLOY_CRONTAB = False

# Should the service configurations be installed on the servers?
# If True, DEPLOY_TO_SERVERS must also be True
DEPLOY_SERVICES = True

UWSGI_SOCKET_PATH = '/tmp/%s.uwsgi.sock' % PROJECT_FILENAME

# Services are the server-side services we want to enable and configure.
# A three-tuple following this format:
# (service name, service deployment path, service config file extension)
SERVER_SERVICES = [
    #('app', SERVER_REPOSITORY_PATH, 'ini'),
    ('uwsgi', '/etc/init', 'conf'),
    ('deploy', '/etc/init', 'conf'),
    ('nginx', '/etc/nginx/locations-enabled', 'conf'),
]

# These variables will be set at runtime. See configure_targets() below
S3_BUCKET = None
S3_BASE_URL = None
S3_DEPLOY_URL = None
SERVERS = []
SERVER_BASE_URL = None
SERVER_LOG_PATH = None
DEBUG = True

"""
COPY EDITING
"""
COPY_GOOGLE_DOC_KEY = '1kFDuz82cQRmdleJEyrLLdK8vPeU6ByBmCH6r7-FuwJQ'
COPY_PATH = 'data/copy.xlsx'

CALENDAR_GOOGLE_DOC_KEY = '1y1JPSwF1MfeK1gW1eH4q4IQxCmB4iuJ-TgIDW12fnfM'
CALENDAR_PATH = 'data/calendar.xlsx'

CARD_GOOGLE_DOC_KEYS = {
    'get_caught_up': {
        'key': '1XJ0Bhi39rm2fAvCGWY_sts1QjMV8d4ddgzP8O_B_sK0',
        'path': 'data/get_caught_up.html',
    },
    'title': {
        'key': '1CzxEsbq3mrEeXpcy4Z14UNj0fnLQHeZcrTr0a1xnQ1Q',
        'path': 'data/title.html',
    },
    'what_happened': {
        'key': '1ayCXdRxQOrFTU58NlHS_N1vipGRatEo7DBQxLwCFRy4',
        'path': 'data/what_happened.html',
    },
    'whats_happening': {
        'key': '1qjeJecYhG0SjXh896E6gMKrcI6XATmlPgAHYIxDd5Hk',
        'path': 'data/whats_happening.html',
    },
    'live_audio': {
        'key': '15rfnjqBwutimoJk8S9jq7LM5L1QCTQwycVaN_OY5H4s',
        'path': 'data/live_audio.html',
    },
    'podcast': {
        'key': '16KdA1yhGln1oh_3lnop4gfUuNAWxTtCOXeQOBSFnJPQ',
        'path': 'data/podcast.html',
    }
}

"""
SHARING
"""
SHARE_URL = 'http://%s/%s/' % (PRODUCTION_S3_BUCKET, PROJECT_SLUG)

"""
ADS
"""

NPR_DFP = {
    'STORY_ID': '1002',
    'TARGET': 'homepage',
    'ENVIRONMENT': 'NPRTEST',
    'TESTSERVER': 'false'
}

"""
SERVICES
"""
NPR_GOOGLE_ANALYTICS = {
    'ACCOUNT_ID': 'UA-5828686-4',
    'DOMAIN': PRODUCTION_S3_BUCKET,
    'TOPICS': 'P1014,1001,1003,139482413,139544303,1091', # e.g. '1014,3,1003,1002,1001'
    'PRIMARY_TOPIC': 'Politics'
}

VIZ_GOOGLE_ANALYTICS = {
    'ACCOUNT_ID': 'UA-5828686-80'
}

DISQUS_API_KEY = 'tIbSzEhGBE9NIptbnQWn4wy1gZ546CsQ2IHHtxJiYAceyyPoAkDkVnQfCifmCaQW'
DISQUS_UUID = '5d97b454-ae74-11e5-b1cf-80e65003a150'

"""
NEWSLETTER CONFIGURATION
"""

# Timeout (ms)
NEWSLETTER_POST_TIMEOUT = 10000

"""
OAUTH
"""

GOOGLE_OAUTH_CREDENTIALS_PATH = '~/.google_oauth_credentials'

authomatic_config = {
    'google': {
        'id': 1,
        'class_': oauth2.Google,
        'consumer_key': os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
        'consumer_secret': os.environ.get('GOOGLE_OAUTH_CONSUMER_SECRET'),
        'scope': ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/userinfo.email'],
        'offline': True,
    },
}

authomatic = Authomatic(authomatic_config, os.environ.get('AUTHOMATIC_SALT'))

"""
Election configuration
"""
NEXT_ELECTION_DATE = '2016-04-09'
ELEX_FLAGS = ''
ELEX_DELEGATE_FLAGS = ''

DELEGATE_ESTIMATES = {
    'Dem': 2383,
    'GOP': 1237,
}

DROPPED_OUT = ['60208', '60339', '60051', '45650', '1239', '1187', '64509', '53044']

DELEGATE_TIMESTAMP_FILE = './.delegates_updated'

LIVESTREAM_POINTER_FILE = 'http://www.npr.org/streams/mp3/nprlive1.m3u'

"""
Daemon configuration
"""
LOAD_COPY_INTERVAL = 15
LOAD_RESULTS_INTERVAL = 30
LOAD_DOCS_INTERVAL = 30
CARD_DEPLOY_INTERVAL = 60
SITE_ARCHIVE_INTERVAL = 3600
LOAD_DELEGATES_INTERVAL = 3600



"""
Logging
"""
LOG_FORMAT = '%(levelname)s:%(name)s:%(asctime)s: %(message)s'

"""
Utilities
"""
def get_secrets():
    """
    A method for accessing our secrets.
    """
    secrets_dict = {}

    for k,v in os.environ.items():
        if k.startswith(PROJECT_SLUG):
            k = k[len(PROJECT_SLUG) + 1:]
            secrets_dict[k] = v

    return secrets_dict

def configure_targets(deployment_target):
    """
    Configure deployment targets. Abstracted so this can be
    overriden for rendering before deployment.
    """
    global S3_BUCKET
    global S3_BASE_URL
    global S3_DEPLOY_URL
    global SERVERS
    global SERVER_BASE_URL
    global SERVER_LOG_PATH
    global DEBUG
    global DEPLOYMENT_TARGET
    global DISQUS_SHORTNAME
    global ASSETS_MAX_AGE
    global NEWSLETTER_POST_URL
    global LOG_LEVEL
    global NEXT_ELECTION_DATE
    global ELEX_FLAGS
    global ELEX_DELEGATE_FLAGS
    global LOAD_COPY_INTERVAL
    global LOAD_DOCS_INTERVAL
    global LOAD_RESULTS_INTERVAL
    global CARD_DEPLOY_INTERVAL
    global SITE_ARCHIVE_INTERVAL
    global LOAD_DELEGATES_INTERVAL
    global COPY_PATH
    global CALENDAR_PATH
    global CARD_GOOGLE_DOC_KEYS
    global database

    secrets = get_secrets()

    """
    Database
    """
    database = {
        'PGDATABASE': PROJECT_SLUG,
        'PGUSER': secrets.get('POSTGRES_USER', PROJECT_SLUG),
        'PGPASSWORD': secrets.get('POSTGRES_PASSWORD', PROJECT_SLUG),
        'PGHOST': secrets.get('POSTGRES_HOST', 'localhost'),
        'PGPORT': secrets.get('POSTGRES_PORT', '5432')
    }

    if deployment_target == 'production':
        S3_BUCKET = 'elections.npr.org'
        S3_BASE_URL = 'http://elections.npr.org'
        S3_DEPLOY_URL = 's3://elections.npr.org'
        SERVERS = PRODUCTION_SERVERS
        SERVER_BASE_URL = 'http://%s/%s' % (SERVERS[0], PROJECT_SLUG)
        SERVER_LOG_PATH = '/var/log/%s' % PROJECT_FILENAME
        DISQUS_SHORTNAME = 'npr-news'
        DEBUG = False
        ASSETS_MAX_AGE = 86400
        NEWSLETTER_POST_URL = 'http://www.npr.org/newsletter/subscribe/politics'
        LOG_LEVEL = logging.DEBUG
        ELEX_FLAGS = ''
        ELEX_DELEGATE_FLAGS = ''
        LOAD_COPY_INTERVAL = 30
        LOAD_RESULTS_INTERVAL = 30
        LOAD_DOCS_INTERVAL = 30
        CARD_DEPLOY_INTERVAL = 30
        SITE_ARCHIVE_INTERVAL = 3600
        LOAD_DELEGATES_INTERVAL = 600
    elif deployment_target == 'staging':
        S3_BUCKET = 'stage-elections16.apps.npr.org'
        S3_BASE_URL = 'http://stage-elections16.apps.npr.org.s3-website-us-east-1.amazonaws.com'
        S3_DEPLOY_URL = 's3://stage-elections16.apps.npr.org'
        SERVERS = STAGING_SERVERS
        SERVER_BASE_URL = 'http://%s/%s' % (SERVERS[0], PROJECT_SLUG)
        SERVER_LOG_PATH = '/var/log/%s' % PROJECT_FILENAME
        DISQUS_SHORTNAME = 'nprviz-test'
        DEBUG = True
        ASSETS_MAX_AGE = 20
        NEWSLETTER_POST_URL = 'http://www.npr.org/newsletter/subscribe/politics'
        LOG_LEVEL = logging.DEBUG
        ELEX_FLAGS = ''
        ELEX_DELEGATE_FLAGS = ''  #'--delegate-sum-file tests/data/20160118_delsum.json --delegate-super-file tests/data/20160118_delsuper.json'
        LOAD_COPY_INTERVAL = 15
        LOAD_RESULTS_INTERVAL = 300
        LOAD_DOCS_INTERVAL = 30
        CARD_DEPLOY_INTERVAL = 15
        SITE_ARCHIVE_INTERVAL = 0
        LOAD_DELEGATES_INTERVAL = 0
    elif deployment_target == 'test':
        S3_BUCKET = 'stage-elections16.apps.npr.org'
        S3_BASE_URL = 'http://stage-elections16.apps.npr.org.s3-website-us-east-1.amazonaws.com'
        S3_DEPLOY_URL = 's3://stage-elections16.apps.npr.org'
        SERVERS = STAGING_SERVERS
        SERVER_BASE_URL = 'http://%s/%s' % (SERVERS[0], PROJECT_SLUG)
        SERVER_LOG_PATH = '/var/log/%s' % PROJECT_FILENAME
        DISQUS_SHORTNAME = 'nprviz-test'
        DEBUG = True
        ASSETS_MAX_AGE = 20
        NEWSLETTER_POST_URL = 'http://stage1.npr.org/newsletter/subscribe/politics'
        LOG_LEVEL = logging.DEBUG
        ELEX_FLAGS = '-d tests/data/ap_elections_loader_recording-1456884323.json'
        ELEX_DELEGATE_FLAGS = '--delegate-sum-file tests/data/20160118_delsum.json --delegate-super-file tests/data/20160118_delsuper.json'
        COPY_PATH = 'tests/data/docs/copy.xlsx'
        CALENDAR_PATH = 'tests/data/docs/calendar.xlsx'
        CARD_GOOGLE_DOC_KEYS = {
            'get_caught_up': {
                'key': '1XJ0Bhi39rm2fAvCGWY_sts1QjMV8d4ddgzP8O_B_sK0',
                'path': 'tests/data/docs/get_caught_up.html',
            },
            'title': {
                'key': '1CzxEsbq3mrEeXpcy4Z14UNj0fnLQHeZcrTr0a1xnQ1Q',
                'path': 'tests/data/docs/title.html',
            },
            'what_happened': {
                'key': '1ayCXdRxQOrFTU58NlHS_N1vipGRatEo7DBQxLwCFRy4',
                'path': 'tests/data/docs/what_happened.html',
            },
            'whats_happening': {
                'key': '1qjeJecYhG0SjXh896E6gMKrcI6XATmlPgAHYIxDd5Hk',
                'path': 'tests/data/docs/whats_happening.html',
            },
            'live_audio': {
                'key': '15rfnjqBwutimoJk8S9jq7LM5L1QCTQwycVaN_OY5H4s',
                'path': 'tests/data/docs/live_audio.html',
            },
            'podcast': {
                'key': '16KdA1yhGln1oh_3lnop4gfUuNAWxTtCOXeQOBSFnJPQ',
                'path': 'tests/data/docs/podcast.html',
            }
        }
        database['PGDATABASE'] = '{0}_test'.format(database['PGDATABASE'])
        database['PGUSER'] = '{0}_test'.format(database['PGUSER'])

    else:
        S3_BUCKET = None
        S3_BASE_URL = 'http://127.0.0.1:8000'
        S3_DEPLOY_URL = None
        SERVERS = []
        SERVER_BASE_URL = 'http://127.0.0.1:8001/%s' % PROJECT_SLUG
        SERVER_LOG_PATH = '/tmp'
        DISQUS_SHORTNAME = 'nprviz-test'
        DEBUG = True
        ASSETS_MAX_AGE = 20
        NEWSLETTER_POST_URL = 'http://stage1.npr.org/newsletter/subscribe/politics'
        LOG_LEVEL = logging.DEBUG
        ELEX_FLAGS = ''
        ELEX_DELEGATE_FLAGS = '--delegate-sum-file tests/data/20160118_delsum.json --delegate-super-file tests/data/20160118_delsuper.json'
        LOAD_COPY_INTERVAL = 15
        LOAD_RESULTS_INTERVAL = 15
        LOAD_DOCS_INTERVAL = 30
        CARD_DEPLOY_INTERVAL = 20
        SITE_ARCHIVE_INTERVAL = 0
        LOAD_DELEGATES_INTERVAL = 3600

    DEPLOYMENT_TARGET = deployment_target

"""
Run automated configuration
"""
DEPLOYMENT_TARGET = os.environ.get('DEPLOYMENT_TARGET', None)

configure_targets(DEPLOYMENT_TARGET)
