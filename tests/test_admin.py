#!/usr/bin/env python

import app_config
import json
import unittest

from admin import *
from fabfile import data
from models import models
from peewee import *
from playhouse.test_utils import test_database

test_db = PostgresqlDatabase(app_config.database['test_name'])

class FilterResultsTestCase(unittest.TestCase):
    """
    Testing filtering for state-level results
    """
    def test_results_filtering(self):
        with test_database(test_db, [models.Result, models.Call], create_tables=True):
            data.load_local_results('tests/data/elex.csv')
            data.create_calls()

            filtered = utils.filter_results()
            self.assertEqual(filtered.count(), 18)

    def test_results_grouping(self):
        with test_database(test_db, [models.Result, models.Call], create_tables=True):
            data.load_local_results('tests/data/elex.csv')
            data.create_calls()

            filtered = utils.filter_results()
            grouped = utils.group_results_by_race(filtered)
            self.assertEqual(len(grouped), 2)

class CallRacesTestCase(unittest.TestCase):
    """
    Testing race calling logic
    """
    def setUp(self):
        self.test_app = admin.app.test_client()

    def send_ap_post(self):
        response = self.test_app.post(
            '/%s/calls/accept-ap' % app_config.PROJECT_SLUG,
            data={
                'race_id': '16957'
            }
        )

        results = models.Result.select().where(
            models.Result.level == 'state',
            models.Result.raceid == '16957'
        )

        return results

    def send_npr_post(self):
        response = self.test_app.post(
            '/%s/calls/call-npr' % app_config.PROJECT_SLUG,
            data={
                'race_id': '16957',
                'result_id': '16957-polid-1239-1'
            }
        )

        result = models.Result.get(models.Result.id == '16957-polid-1239-1')

        race_results = models.Result.select().where(
            models.Result.level == 'state',
            models.Result.raceid == '16957'
        )
        return result, race_results

    def test_accepting_ap(self):
        with test_database(test_db, [models.Result, models.Call], create_tables=True):
            data.load_local_results('tests/data/elex.csv')
            data.create_calls()

            true_results = self.send_ap_post()
            for result in true_results:
                self.assertTrue(result.call[0].accept_ap)

    def test_calling_npr(self):
        with test_database(test_db, [models.Result, models.Call], create_tables=True):
            data.load_local_results('tests/data/elex.csv')
            data.create_calls()

            called_result, race_results = self.send_npr_post()
            self.assertTrue(called_result.call[0].override_winner)

            for result in race_results:
                self.assertFalse(result.call[0].accept_ap)


if __name__ == '__main__':
    unittest.main()
