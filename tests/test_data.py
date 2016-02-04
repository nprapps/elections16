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

    def test_results_collation(self):
        with test_database(test_db, [models.Result, models.Call], create_tables=True):
            data.load_local_results('tests/data/elex.csv')
            data.create_calls()

            for party in ['Dem', 'GOP']:
                results = models.Result.select().where(
                    (models.Result.party == party)
                )
                filtered, other_votecount, other_votepct = utils.collate_other_candidates(list(results), party)
                filtered_length = len(filtered)
                if party == 'dem':
                    whitelist_length = utils.DEM_CANDIDATES
                    self.assertEqual(filtered_length, whitelist_length)
                elif party == 'gop':
                    whitelist_length = utils.GOP_CANDIDATES
                    self.assertEqual(filtered_length, whitelist_length)





if __name__ == '__main__':
    unittest.main()
