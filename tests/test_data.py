#!/usr/bin/env python

import app_config
import unittest

from fabfile import data
from models import models
from peewee import *
from playhouse.test_utils import test_database

test_db = PostgresqlDatabase(app_config.DATABASE['test_name'])

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


if __name__ == '__main__':
    unittest.main()
