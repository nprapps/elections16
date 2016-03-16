#!/usr/bin/env python

import app_config
import calendar
import unittest

from app import utils
from fabfile import data
from models import models
from peewee import *
from time import time
from datetime import datetime

class ResultsLoadingTestCase(unittest.TestCase):
    """
    Test bootstrapping postgres database
    """
    def setUp(self):
        data.load_results()
        data.create_calls()
        data.create_race_meta()

    def test_results_loading(self):
        results_length = models.Result.select().count()
        self.assertEqual(results_length, 29882)

    def test_calls_creation(self):
        calls_length = models.Call.select().count()
        self.assertEqual(calls_length, 185)

    def test_race_meta_creation(self):
        race_meta_length = models.RaceMeta.select().count()
        self.assertEqual(race_meta_length, 185)

    def test_multiple_calls_creation(self):
        data.create_calls()
        calls_length = models.Call.select().count()
        self.assertEqual(calls_length, 185)

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
        # whitelist_length times number of races
        self.assertEqual(filtered_length, whitelist_length * 11)

    def test_results_collation_gop(self):
        results = models.Result.select().where(
            (models.Result.party == 'GOP'),
            (models.Result.level == 'state')
        )

        filtered, other_votecount, other_votepct = utils.collate_other_candidates(list(results), 'GOP')
        filtered_length = len(filtered)
        whitelist_length = len(utils.GOP_CANDIDATES)
        # whitelist_length times number of races
        self.assertEqual(filtered_length, whitelist_length * 11)

    def test_vote_tally(self):
        tally = utils.tally_results('12044')
        self.assertEqual(tally, 167554)

    def test_last_updated_precinctsreporting(self):
        races = utils.get_results('gop', app_config.NEXT_ELECTION_DATE)
        last_updated = utils.get_last_updated(races)
        self.assertEqual(last_updated, datetime(2016, 3, 2, 2, 4, 50))

    def test_last_updated_before(self):
        models.Result.update(precinctsreporting=0).execute()
        races = utils.get_results('gop', app_config.NEXT_ELECTION_DATE)
        last_updated = utils.get_last_updated(races)
        last_updated_ts = calendar.timegm(last_updated.timetuple())
        now = time()
        self.assertAlmostEqual(now, last_updated_ts, delta=10)

    def test_last_updated_called_noprecincts(self):
        models.Result.update(precinctsreporting=0).execute()
        models.Call.update(override_winner=True).where(models.Call.call_id == '12044-polid-1746-state-1').execute()
        races = utils.get_results('dem', app_config.NEXT_ELECTION_DATE)
        last_updated = utils.get_last_updated(races)
        self.assertEqual(last_updated, datetime(2016, 3, 2, 2, 4, 1))

    def test_poll_closing_grouping(self):
        races = utils.get_results('gop', app_config.NEXT_ELECTION_DATE)
        poll_closings = utils.group_poll_closings(races)
        poll_closings_length = len(poll_closings)
        self.assertEqual(poll_closings_length, 5)

    def test_poll_closing_listing(self):
        races = utils.get_results('dem', app_config.NEXT_ELECTION_DATE)
        poll_closings = utils.group_poll_closings(races)
        nine_pm_closings = poll_closings[4]['races']
        self.assertEqual(len(nine_pm_closings), 2)



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
