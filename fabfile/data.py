#!/usr/bin/env python

"""
Commands that update or process the application data.
"""
import app_config
app_config.configure_targets('test')

from app.gdoc import get_google_doc
from elex.api import Elections
from fabric.api import local, task, settings, shell_env
from fabric.state import env
from models import models

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
    with settings(warn_only=True):
        if env.get('settings'):
            servers.stop_service('uwsgi')
            servers.stop_service('deploy')

        with shell_env(**app_config.database):
            local('dropdb --if-exists %s' % app_config.database['PGDATABASE'])

        if not env.get('settings'):
            local('psql -c "DROP USER IF EXISTS %s;"' % app_config.database['PGUSER'])
            local('psql -c "CREATE USER %s WITH SUPERUSER PASSWORD \'%s\';"' % (app_config.database['PGUSER'], app_config.database['PGPASSWORD']))

        with shell_env(**app_config.database):
            local('createdb %s' % app_config.database['PGDATABASE'])

        if env.get('settings'):
            servers.start_service('uwsgi')
            servers.start_service('deploy')

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
        local('elex races %s %s | psql %s -c "COPY race FROM stdin DELIMITER \',\' CSV HEADER;"' % (election_date, app_config.ELEX_FLAGS, app_config.database['name']))
        local('elex reporting-units %s %s | psql %s -c "COPY reportingunit FROM stdin DELIMITER \',\' CSV HEADER;"' % (election_date, app_config.ELEX_FLAGS, app_config.database['name']))
        local('elex candidates %s %s | psql %s -c "COPY candidate FROM stdin DELIMITER \',\' CSV HEADER;"' % (election_date, app_config.ELEX_FLAGS, app_config.database['name']))
        local('elex ballot-measures %s %s | psql %s -c "COPY ballotposition FROM stdin DELIMITER \',\' CSV HEADER;"' % (election_date, app_config.ELEX_FLAGS, app_config.database['name']))


@task
def delete_results():
    """
    Delete results without droppping database.
    """
    with shell_env(**app_config.database):
        local('psql {0} -c "set session_replication_role = replica; DELETE FROM result; set session_replication_role = default;"'.format(app_config.database['PGDATABASE']))


@task
def load_results(election_date=app_config.NEXT_ELECTION_DATE):
    """
    Load AP results. Defaults to next election, or specify a date as a parameter.
    """
    local('mkdir -p .data')
    cmd = 'elex results {0} {1} > .data/results.csv'.format(election_date, app_config.ELEX_FLAGS)
    with shell_env(**app_config.database):
        with settings(warn_only=True):
            cmd_output = local(cmd, capture=True)

        if cmd_output.succeeded:
            print("LOADING RESULTS")
            delete_results()
            local('cat .data/results.csv | psql {0} -c "COPY result FROM stdin DELIMITER \',\' CSV HEADER;"'.format(app_config.database['PGDATABASE']))
        else:
            print("ERROR GETTING RESULTS")
            print(cmd_output.stderr)


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
        local('psql %s -c "COPY result FROM \'%s\' DELIMITER \',\' CSV HEADER;"' % (app_config.database['test_name'], os.path.join(root_path, file_path)))


@task
def create_calls():
    """
    Create database of race calls for all races in results data.
    """
    models.Call.delete().execute()

    results = models.Result.select().where(
        models.Result.level == 'state'
    )

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
        'PGHOST': app_config.database['host'],
        'PGPORT': app_config.database['port'],
        'PGDATABASE': app_config.database['name'],
    }
    if app_config.database['user']:
        vars['PGUSER'] = app_config.database['user']

    if app_config.database['password']:
        vars['PGPASSWORD'] = app_config.database['password']

    return vars
