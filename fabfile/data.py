#!/usr/bin/env python

"""
Commands that update or process the application data.
"""
import app_config

from oauth.blueprint import get_document
from app.utils import set_delegates_updated_time
from fabric.api import local, task, settings, shell_env
from fabric.state import env
from models import models

import codecs
import copytext
import servers

TEST_GOOGLE_DOC_KEY = '1uXy5ZKRZf3rWJ9ge1DWX2jhOeduvFGf9jfK0x3tmEqE'


@task
def bootstrap_db():
    """
    Build the database.
    """
    create_db()
    create_tables()
    load_results()
    create_calls()
    create_race_meta()
    load_delegates()


@task
def create_db():
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


@task
def create_tables():
    models.Result.create_table()
    models.Call.create_table()
    models.Race.create_table()
    models.ReportingUnit.create_table()
    models.Candidate.create_table()
    models.BallotPosition.create_table()
    models.CandidateDelegates.create_table()
    models.RaceMeta.create_table()


@task
def load_init_data():
    """
    Bootstrap races, candidates, reporting units, and ballot positions.
    """
    election_date = app_config.NEXT_ELECTION_DATE
    with shell_env(**app_config.database):
        local('elex races %s %s | psql %s -c "COPY race FROM stdin DELIMITER \',\' CSV HEADER;"' % (election_date, app_config.ELEX_FLAGS, app_config.database['PGDATABASE']))
        local('elex reporting-units %s %s | psql %s -c "COPY reportingunit FROM stdin DELIMITER \',\' CSV HEADER;"' % (election_date, app_config.ELEX_FLAGS, app_config.database['PGDATABASE']))
        local('elex candidates %s %s | psql %s -c "COPY candidate FROM stdin DELIMITER \',\' CSV HEADER;"' % (election_date, app_config.ELEX_FLAGS, app_config.database['PGDATABASE']))
        local('elex ballot-measures %s %s | psql %s -c "COPY ballotposition FROM stdin DELIMITER \',\' CSV HEADER;"' % (election_date, app_config.ELEX_FLAGS, app_config.database['PGDATABASE']))


@task
def delete_results():
    """
    Delete results without droppping database.
    """
    with shell_env(**app_config.database):
        local('psql {0} -c "set session_replication_role = replica; DELETE FROM result; set session_replication_role = default;"'.format(app_config.database['PGDATABASE']))


@task
def delete_delegates():
    """
    Delete results without droppping database.
    """
    with shell_env(**app_config.database):
        local('psql {0} -c "set session_replication_role = replica; DELETE FROM candidatedelegates; set session_replication_role = default;"'.format(app_config.database['PGDATABASE']))


@task
def load_results():
    """
    Load AP results. Defaults to next election, or specify a date as a parameter.
    """
    election_date = app_config.NEXT_ELECTION_DATE
    local('mkdir -p .data')
    cmd = 'elex results {0} --results-level state {1} > .data/results.csv'.format(election_date, app_config.ELEX_FLAGS)
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
def load_delegates():
    """
    Load AP results. Defaults to next election, or specify a date as a parameter.
    """
    local('mkdir -p .data')
    cmd = 'elex delegates {0} > .data/delegates.csv'.format(app_config.ELEX_DELEGATE_FLAGS)
    with shell_env(**app_config.database):
        with settings(warn_only=True):
            cmd_output = local(cmd, capture=True)

        if cmd_output.succeeded:
            print("LOADING DELEGATES")
            delete_delegates()
            local('cat .data/delegates.csv | psql {0} -c "COPY candidatedelegates FROM stdin DELIMITER \',\' CSV HEADER;"'.format(app_config.database['PGDATABASE']))
            set_delegates_updated_time()
        else:
            print("ERROR GETTING DELEGATES")
            print(cmd_output.stderr)


@task
def create_calls():
    """
    Create database of race calls for all races in results data.
    """
    models.Call.delete().execute()

    results = models.Result.select().where(
        models.Result.level == 'state',
        models.Result.officename == 'President'
    )

    for result in results:
        models.Call.create(call_id=result.id)

@task
def create_race_meta():
    models.RaceMeta.delete().execute()

    results = models.Result.select().where(
        models.Result.level == 'state',
        models.Result.officename == 'President'
    )

    calendar = copytext.Copy(app_config.CALENDAR_PATH)
    calendar_sheet = calendar['data']

    for row in calendar_sheet._serialize():
        if not row.get('full_poll_closing_time'):
            continue

        results = models.Result.select().where(
                models.Result.level == 'state',
                models.Result.statename == row['state_name'],
                models.Result.officename == 'President'
        )

        for result in results:
            race_type = row['type'].lower()
            models.RaceMeta.create(
                    result_id=result.id,
                    race_type=race_type,
                    poll_closing=row['full_poll_closing_time'],
                    order=row['ordinal']
            )


@task
def download_test_gdoc():
    """
    Get the latest testing Google Doc and write to 'tests/data/testdoc.html'.
    """
    get_document(TEST_GOOGLE_DOC_KEY, 'tests/data/testdoc.html')
