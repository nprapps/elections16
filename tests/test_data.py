#!/usr/bin/env python

import app_config
import calendar
import unittest

from app import utils
from fabfile import data
from models import models
from peewee import *
from time import time


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

    def test_vote_tally(self):
        tally = utils.tally_results('gop', app_config.NEXT_ELECTION_DATE)
        self.assertEqual(tally, 186874)


class DelegatesLoadingTestCase(unittest.TestCase):
    """
    Test bootstrapping postgres database
    """
    def setUp(self):
        data.load_delegates()
        self.now = time()

    def test_delegates_timestamp(self):
        filesystem_datetime = utils.get_delegates_updated_time()
        filesystem_ts = calendar.timegm(filesystem_datetime.timetuple())
        # Compare timestamps; can be +/- 10 seconds
        self.assertAlmostEqual(self.now, filesystem_ts, delta=10)

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

    def test_pledged_delegates_percent(self):
        record = models.CandidateDelegates.select().where(
            models.CandidateDelegates.level == 'nation',
            models.CandidateDelegates.last == 'Clinton'
        ).get()
        pledged_delegate_percent = record.pledged_delegates_pct()
        self.assertEqual(pledged_delegate_percent, 8.942065491183879)

    def test_super_delegates_percent(self):
        record = models.CandidateDelegates.select().where(
            models.CandidateDelegates.level == 'nation',
            models.CandidateDelegates.last == 'Clinton'
        ).get()
        super_delegate_percent = record.superdelegates_pct()
        self.assertEqual(super_delegate_percent, 15.071368597816962)

    def test_delegates_deletion(self):
        data.delete_delegates()
        all_records = models.CandidateDelegates.select().count()
        self.assertEqual(all_records, 0)

if __name__ == '__main__':
    unittest.main()
