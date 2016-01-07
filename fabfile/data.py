#!/usr/bin/env python

"""
Commands that update or process the application data.
"""
from elex.api.api import Elections
from fabric.api import local, task, require, run, shell_env
from fabric.state import env
from models import models

import app_config
import servers


@task(default=True)
def update():
    """
    Stub function for updating app-specific data.
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
def load_results(election_date=None):
    require('settings', provided_by=['production', 'staging', 'dev'])

    if not election_date:
        next_election = Elections().get_next_election()
        election_date = next_election.serialize().get('electiondate')

    pg_vars = _get_pg_vars()
    with shell_env(**pg_vars):
        local('elex results %s | psql %s -c "COPY result FROM stdin DELIMITER \',\' CSV HEADER;"' % (election_date, app_config.DATABASE['name']))


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
