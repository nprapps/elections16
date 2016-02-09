#!/usr/bin/env python

import unittest

import app_config
from app import utils
from fabfile import data
from models import models
from peewee import *


class ResultsLoadingTestCase(unittest.TestCase):
    """
    Test bootstrapping postgres database
    """
    def setUp(self):
        data.load_results()
        data.create_calls()

    def test_results_loading(self):
        results_length = models.Result.select().count()
        self.assertEqual(results_length, 1800)

    def test_calls_creation(self):
        calls_length = models.Call.select().count()
        self.assertEqual(calls_length, 18)

    def test_multiple_calls_creation(self):
        data.create_calls()
        calls_length = models.Call.select().count()
        self.assertEqual(calls_length, 18)

    def test_results_deletion(self):
        data.delete_results()
        results_length = models.Result.select().count()
        self.assertEqual(results_length, 0)

    def test_results_collation_dem(self):
        results = models.Result.select().where(
            (models.Result.party == 'Dem'),
            (models.Result.level == 'state')
        )
        filtered, other_votecount, other_votepct = utils.collate_other_candidates(list(results), 'Dem')
        filtered_length = len(filtered)
        whitelist_length = len(utils.DEM_CANDIDATES)
        self.assertEqual(filtered_length, whitelist_length)

    def test_results_collation_gop(self):
        results = models.Result.select().where(
            (models.Result.party == 'GOP'),
            (models.Result.level == 'state')
        )

        filtered, other_votecount, other_votepct = utils.collate_other_candidates(list(results), 'GOP')
        filtered_length = len(filtered)
        whitelist_length = len(utils.GOP_CANDIDATES)
        self.assertEqual(filtered_length, whitelist_length)


class DelegatesLoadingTestCase(unittest.TestCase):
    """
    Test bootstrapping postgres database
    """
    def setUp(self):
        data.load_delegates()

    def test_delegates_length(self):
        results_length = models.CandidateDelegates.select().where(
            models.CandidateDelegates.level == 'nation'
        ).count()
        self.assertEqual(results_length, 30)

    def test_delegate_count(self):
        record = models.CandidateDelegates.select().where(
            models.CandidateDelegates.level == 'nation',
            models.CandidateDelegates.last == 'Fiorina'
        ).get()

        self.assertEqual(record.delegates_count, 1)

    def test_superdelegate_count(self):
        record = models.CandidateDelegates.select().where(
            models.CandidateDelegates.level == 'nation',
            models.CandidateDelegates.last == 'Clinton'
        ).get()

        self.assertEqual(record.superdelegates_count, 359)

    def test_delegates_deletion(self):
        data.delete_delegates()
        all_records = models.CandidateDelegates.select().count()
        self.assertEqual(all_records, 0)

if __name__ == '__main__':
    unittest.main()
