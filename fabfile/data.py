#!/usr/bin/env python

"""
Commands that update or process the application data.
"""
from app.gdoc import get_google_doc
from elex.api.api import Elections
from fabric.api import local, task, shell_env
from fabric.state import env
from models import models

import app_config
import codecs
import os
import servers

TEST_GOOGLE_DOC_KEY = '1uXy5ZKRZf3rWJ9ge1DWX2jhOeduvFGf9jfK0x3tmEqE'


@task(default=True)
def update():
    """
    Stub function for updating app-specific data. Not currently implemented.
    """
    pass


@task
def bootstrap_db():
    """
    Build the database.
    """
    if env.get('settings'):
        servers.stop_service('uwsgi')

    pg_vars = _get_pg_vars()
    with shell_env(**pg_vars):
        local('dropdb --if-exists %s' % app_config.DATABASE['name'])
        local('createdb %s' % app_config.DATABASE['name'])
        local('dropdb --if-exists %s' % app_config.DATABASE['test_name'])
        local('createdb %s' % app_config.DATABASE['test_name'])


    if env.get('settings'):
        servers.start_service('uwsgi')

    models.Result.create_table()
    models.Call.create_table()
    models.Race.create_table()
    models.ReportingUnit.create_table()
    models.Candidate.create_table()
    models.BallotPosition.create_table()


@task
def bootstrap_data(election_date=None):
    """
    Bootstrap races, candidates, reporting units, and ballot positions.
    """
    if not election_date:
        next_election = Elections().get_next_election()
        election_date = next_election.serialize().get('electiondate')

    pg_vars = _get_pg_vars()
    with shell_env(**pg_vars):
        local('elex races %s | psql %s -c "COPY race FROM stdin DELIMITER \',\' CSV HEADER;"' % (election_date, app_config.DATABASE['name']))
        local('elex reporting-units %s | psql %s -c "COPY reportingunit FROM stdin DELIMITER \',\' CSV HEADER;"' % (election_date, app_config.DATABASE['name']))
        local('elex candidates %s | psql %s -c "COPY candidate FROM stdin DELIMITER \',\' CSV HEADER;"' % (election_date, app_config.DATABASE['name']))
        local('elex ballot-measures %s | psql %s -c "COPY ballotposition FROM stdin DELIMITER \',\' CSV HEADER;"' % (election_date, app_config.DATABASE['name']))


@task
def delete_results(election_date=None, test_db=False):
    """
    Delete results without droppping database.
    """

    if not test_db:
        db_name = app_config.DATABASE['name']
        if not election_date:
            next_election = Elections().get_next_election()
            election_date = next_election.serialize().get('electiondate')
        clause = "WHERE electiondate='%s'" % election_date
    else:
        db_name = app_config.DATABASE['test_name']
        clause = ''

    pg_vars = _get_pg_vars()
    with shell_env(**pg_vars):
        local('psql %s -c "set session_replication_role = replica; DELETE FROM result %s; set session_replication_role = default;"' % (db_name, clause))


@task
def load_results(election_date=None):
    """
    Load AP results. Defaults to next election, or specify a date as a parameter.
    """
    if not election_date:
        next_election = Elections().get_next_election()
        election_date = next_election.serialize().get('electiondate')

    pg_vars = _get_pg_vars()
    with shell_env(**pg_vars):
        local('elex results %s | psql %s -c "COPY result FROM stdin DELIMITER \',\' CSV HEADER;"' % (election_date, app_config.DATABASE['name']))


@task
def load_local_results(file_path):
    """
    Load AP results from local file.
    """

    # Force root path every time
    fab_path = os.path.realpath(os.path.dirname(__file__))
    root_path = os.path.join(fab_path, '..')
    os.chdir(root_path)

    pg_vars = _get_pg_vars()
    with shell_env(**pg_vars):
        local('psql %s -c "COPY result FROM \'%s\' DELIMITER \',\' CSV HEADER;"' % (app_config.DATABASE['test_name'], os.path.join(root_path, file_path)))


@task
def create_calls():
    """
    Create database of race calls for all races in results data.
    """
    results = models.Result.select()
    for result in results:
        models.Call.create(call_id=result.id)


@task
def download_test_gdoc():
    """
    Get the latest testing Google Doc and write to 'tests/data/testdoc.html'.
    """
    html_string = get_google_doc(TEST_GOOGLE_DOC_KEY)
    with codecs.open('tests/data/testdoc.html', 'w', 'utf-8') as f:
        f.write(html_string)


def _get_pg_vars():
    """
    Construct a dict of postgres environment variables to set in shell for
    fabric commands
    """
    vars = {
        'PGHOST': app_config.DATABASE['host'],
        'PGPORT': app_config.DATABASE['port'],
        'PGDATABASE': app_config.DATABASE['name'],
    }
    if app_config.DATABASE['user']:
        vars['PGUSER'] = app_config.DATABASE['user']

    if app_config.DATABASE['password']:
        vars['PGPASSWORD'] = app_config.DATABASE['password']

    return vars
