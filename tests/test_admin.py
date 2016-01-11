#!/usr/bin/env python

import app_config
import json
import unittest

from admin import *
from fabfile import data
from models import models
from peewee import *
from playhouse.test_utils import test_database

test_db = PostgresqlDatabase('elections16test')

class FilterResultsTestCase(unittest.TestCase):
    """
    Testing filtering for state-level results
    """

    def test_results_filtering(self):
        with test_database(test_db, [models.Result, models.Call], create_tables=True):
            data.load_local_results('/tests/data/elex.csv')
            data.create_calls()

            filtered = utils.filter_results()
            self.assertEqual(filtered.count(), 20)

    def test_results_grouping(self):
        with test_database(test_db, [models.Result, models.Call], create_tables=True):
            data.load_local_results('/tests/data/elex.csv')
            data.create_calls()

            filtered = utils.filter_results()
            grouped = utils.group_results_by_race(filtered)
            self.assertEqual(len(grouped), 2)

if __name__ == '__main__':
    unittest.main()