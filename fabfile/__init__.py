#!/usr/bin/env python

from datetime import datetime
import json
import logging
import os

from boto.s3.key import Key
from fabric.api import get, local, require, settings, task
from fabric.state import env
from termcolor import colored

import app_config
import copytext

# Other fabfiles
import assets
import data
import daemons
import flat
import issues
import render
import text
import utils

if app_config.DEPLOY_TO_SERVERS:
    import servers

if app_config.DEPLOY_CRONTAB:
    import cron_jobs

# Bootstrap can only be run once, then it's disabled
if app_config.PROJECT_SLUG == '$NEW_PROJECT_SLUG':
    import bootstrap_project

logging.basicConfig(format=app_config.LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(app_config.LOG_LEVEL)

"""
Base configuration
"""
env.user = app_config.SERVER_USER
env.forward_agent = True
env.hosts = []

"""
Environments

Changing environment requires a full-stack test.
An environment points to both a server and an S3
bucket.
"""
@task
def production():
    """
    Run as though on production.
    """
    env.settings = 'production'
    app_config.configure_targets(env.settings)
    env.hosts = app_config.SERVERS

@task
def staging():
    """
    Run as though on staging.
    """
    env.settings = 'staging'
    app_config.configure_targets(env.settings)
    env.hosts = app_config.SERVERS

@task
def dev():
    """
    Run locally.
    """
    env.settings = 'dev'
    app_config.configure_targets(env.settings)


@task
def test():
    """
    Run locally.
    """
    env.settings = 'test'
    app_config.configure_targets(env.settings)

"""
Branches

Changing branches requires deploying that branch to a host.
"""
@task
def stable():
    """
    Work on stable branch.
    """
    env.branch = 'stable'

@task
def master():
    """
    Work on development branch.
    """
    env.branch = 'master'

@task
def branch(branch_name):
    """
    Work on any specified branch.
    """
    env.branch = branch_name

"""
Running the app
"""
@task
def app(port='8000'):
    """
    Serve app/app.py.
    """
    if env.get('settings'):
        local("DEPLOYMENT_TARGET=%s bash -c 'gunicorn -b 0.0.0.0:%s --timeout 3600 --debug --reload --log-file=logs/app.log app:wsgi_app'" % (env.settings, port))
    else:
        local('gunicorn -b 0.0.0.0:%s --timeout 3600 --debug --reload --log-file=logs/app.log app:wsgi_app' % port)

@task
def admin(port='8001'):
    """
    Serve admin/app.py.
    """
    if env.get('settings'):
        local("DEPLOYMENT_TARGET=%s bash -c 'gunicorn -b 0.0.0.0:%s --timeout 3600 --debug --reload --log-file=logs/admin.log admin:wsgi_app'" % (env.settings, port))
    else:
        local('gunicorn -b 0.0.0.0:%s --timeout 3600 --debug --reload --log-file=logs/admin.log admin:wsgi_app' % port)

@task
def tests():
    """
    Run Python unit tests.
    """
    local('nose2 -v tests')

@task
def js_tests():
    """
    Run Karma/Jasmine unit tests.
    """
    render.render_all()
    local('node_modules/karma/bin/karma start www/js/test/karma.conf.js')


"""
Bootstrap
"""


@task
def bootstrap():
    """
    Reset font, db, copy, calendar, and docs.

    Install font, update copy and calendar from Google Spreadsheets, update content from Google Docs, and reset db.
    """
    utils.install_font()
    text.update_copytext()
    text.update_calendar()
    text.update_newsletter()
    text.update_all_docs()
    data.bootstrap_db()


"""
Deployment

Changes to deployment requires a full-stack test. Deployment
has two primary functions: Pushing flat files to S3 and deploying
code to a remote server if required.
"""
@task
def update():
    """
    Update all application data not in repository (copy, assets, etc).
    """
    utils.install_font(force=False)
    text.update_copytext()
    text.update_calendar()
    text.update_newsletter()
    text.update_all_docs()
    assets.sync()


@task
def deploy(remote='origin'):
    """
    Deploy and restart services
    """
    deploy_server(remote)
    servers.fabcast('deploy_client')


@task
def deploy_server(remote='origin'):
    """
    Deploy and restart server
    """
    if app_config.DEPLOY_TO_SERVERS:
        require('branch', provided_by=[stable, master, branch])

        if (app_config.DEPLOYMENT_TARGET == 'production' and env.branch != 'stable'):
            utils.confirm(
                colored("You are trying to deploy the '%s' branch to production.\nYou should really only deploy a stable branch.\nDo you know what you're doing?" % env.branch, "red")
            )

        servers.checkout_latest(remote)

        servers.fabcast('text.update_copytext')
        servers.fabcast('text.update_active_docs')
        servers.fabcast('text.update_calendar')
        servers.fabcast('assets.sync')

        if app_config.DEPLOY_CRONTAB:
            servers.install_crontab()

        if app_config.DEPLOY_SERVICES:
            servers.deploy_confs()

@task
def deploy_client(reload=False):
    """
    Deploy the latest app to S3.
    """
    require('settings', provided_by=[production, staging])

    update()
    render.render_all()
    render.render_current_state(folder='www')

    # Clear files that should never be deployed
    local('rm -rf www/live-data')

    flat.deploy_folder(
        app_config.S3_BUCKET,
        'www',
        '',
        headers={
            'Cache-Control': 'max-age=%i' % app_config.DEFAULT_MAX_AGE
        },
        ignore=['www/assets/*', 'www/live-data/*']
    )

    flat.deploy_folder(
        app_config.S3_BUCKET,
        'www/assets',
        'assets',
        headers={
            'Cache-Control': 'max-age=%i' % app_config.ASSETS_MAX_AGE
        }
    )

    if reload:
        reset_browsers()

    if not check_timestamp():
        reset_browsers()


@task
def deploy_results_data():
    """
    Deploy results cards.
    """
    local('rm -rf .cards_html/data')
    render.render_results_json()
    flat.deploy_folder(
        app_config.S3_BUCKET,
        '.cards_html/data',
        'data',
        headers={
            'Cache-Control': 'max-age=%i' % app_config.DEFAULT_MAX_AGE
        }
    )


@task
def deploy_delegates_data():
    """
    Deploy results cards.
    """
    require('settings', provided_by=[production, staging])

    local('rm -rf .cards_html/data')
    render.render_delegates_json()
    flat.deploy_folder(
        app_config.S3_BUCKET,
        '.cards_html/data',
        'data',
        headers={
            'Cache-Control': 'max-age=%i' % app_config.DEFAULT_MAX_AGE
        }
    )


@task
def deploy_cards():
    """
    Deploy content cards.
    """
    require('settings', provided_by=[production, staging])
    local('rm -rf .cards_html')
    COPY = copytext.Copy(app_config.COPY_PATH)
    if env.settings == 'production':
        state = COPY['meta']['prod_state']['value']
    elif env.settings == 'staging':
        state = COPY['meta']['stage_state']['value']
    else:
        state = COPY['meta']['dev_state']['value']

    script = COPY[state]

    for row in script:
        render.render_card_route(row['function'], row['params'])

    render.render_current_state()
    render.render_index()

    flat.deploy_folder(
        app_config.S3_BUCKET,
        '.cards_html',
        '',
        headers={
            'Cache-Control': 'max-age=%i' % app_config.DEFAULT_MAX_AGE
        }
    )


@task
def archive_site():
    """
    Make a site archive.
    """
    require('settings', provided_by=[production, staging])
    now = datetime.now().strftime('%Y-%m-%d-%H:%M')
    s3archiveurl = 's3://{0}/{1}/backup-{2}/'.format(app_config.ARCHIVE_S3_BUCKET, env.settings, now)
    cmd = 'aws s3 sync {0}/ {1} --acl public-read --source-region us-west-2 --region us-east-1'.format(app_config.S3_DEPLOY_URL, s3archiveurl)
    local(cmd)


@task
def check_timestamp():
    """
    Check if a timestamp file exists.
    """
    require('settings', provided_by=[production, staging])

    bucket = utils.get_bucket(app_config.S3_BUCKET)
    k = Key(bucket)
    k.key = 'live-data/timestamp.json'
    if k.exists():
        return True
    else:
        return False


@task
def reset_browsers():
    """
    Deploy a timestamp so the client will reset their page. For bugfixes
    """
    require('settings', provided_by=[production, staging])

    if not os.path.exists('www/live-data'):
        os.makedirs('www/live-data')

    payload = {}
    now = datetime.now().strftime('%s')
    payload['timestamp'] = now

    with open('www/live-data/timestamp.json', 'w') as f:
        json.dump(payload, f)

    flat.deploy_folder(
        app_config.S3_BUCKET,
        'www/live-data',
        'live-data',
        headers={
            'Cache-Control': 'max-age=%i' % app_config.DEFAULT_MAX_AGE
        }
    )


"""
Oh SH*T!

Fallback helpers
"""


@task
def mirror_gdocs():
    """
    Mirror Google docs from server locally. Use in emergencies.
    """
    require('settings', provided_by=[production, staging])
    remote_data_path = '%(SERVER_PROJECT_PATH)s/repository/data' % app_config.__dict__
    get('%s/*.html' % remote_data_path, 'data')
    local('git add -f data/*.html')
    get('%s/*.xlsx' % remote_data_path, 'data')
    local('git add -f data/*.xlsx')
    print('Downloaded server versions of Google docs to `data` directory.')
    print('Files have been staged to be added to version control:')
    local('git status')
    print('Commit these files, set LOAD_COPY_INTERVAL and LOAD_DOCS_INTERVAL to 0 in app_config, and re-deploy.')

"""
Destruction

Changes to destruction require setup/deploy to a test host in order to test.
Destruction should remove all files related to the project from both a remote
host and S3.
"""

@task
def shiva_the_destroyer():
    """
    Deletes the app from s3
    """
    require('settings', provided_by=[production, staging])

    utils.confirm(
        colored("You are about to destroy everything deployed to %s for this project.\nDo you know what you're doing?')" % app_config.DEPLOYMENT_TARGET, "red")
    )

    with settings(warn_only=True):
        flat.delete_folder(app_config.S3_BUCKET, app_config.PROJECT_SLUG)

        if app_config.DEPLOY_TO_SERVERS:
            servers.delete_project()

            if app_config.DEPLOY_CRONTAB:
                servers.uninstall_crontab()

            if app_config.DEPLOY_SERVICES:
                servers.nuke_confs()
