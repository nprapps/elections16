#!/usr/bin/env python

import app_config
import unittest

from app import utils
from fabfile import data
from models import models
from peewee import *
from playhouse.test_utils import test_database

test_db = PostgresqlDatabase(app_config.database['test_name'])

class ResultsLoadingTestCase(unittest.TestCase):
    """
    Test bootstrapping postgres database
    """
    def test_results_loading(self):
        with test_database(test_db, [models.Result, models.Call], create_tables=True):
            data.load_local_results('tests/data/elex.csv')
            results_length = models.Result.select().count()
            self.assertEqual(results_length, 1800)

    def test_calls_creation(self):
        with test_database(test_db, [models.Result, models.Call], create_tables=True):
            data.load_local_results('tests/data/elex.csv')
            data.create_calls()
            calls_length = models.Call.select().count()
            self.assertEqual(calls_length, 18)

    def test_results_deletion(self):
        with test_database(test_db, [models.Result, models.Call], create_tables=True):
            data.load_local_results('tests/data/elex.csv')
            data.create_calls()
            data.delete_results(test_db=True)
            results_length = models.Result.select().count()
            self.assertEqual(results_length, 0)

    def test_results_collation_dem(self):
        with test_database(test_db, [models.Result, models.Call], create_tables=True):
            data.load_local_results('tests/data/elex.csv')
            data.create_calls()

            results = models.Result.select().where(
                (models.Result.party == 'Dem'),
                (models.Result.level == 'state')
            )
            filtered, other_votecount, other_votepct = utils.collate_other_candidates(list(results), 'Dem')
            filtered_length = len(filtered)
            whitelist_length = len(utils.DEM_CANDIDATES)
            self.assertEqual(filtered_length, whitelist_length)

    def test_results_collation_gop(self):
        with test_database(test_db, [models.Result, models.Call], create_tables=True):
            data.load_local_results('tests/data/elex.csv')
            data.create_calls()

            results = models.Result.select().where(
                (models.Result.party == 'GOP'),
                (models.Result.level == 'state')
            )
            filtered, other_votecount, other_votepct = utils.collate_other_candidates(list(results), 'GOP')
            filtered_length = len(filtered)
            whitelist_length = len(utils.GOP_CANDIDATES)
            self.assertEqual(filtered_length, whitelist_length)



if __name__ == '__main__':
    unittest.main()
