#!/usr/bin/env python
import app
import app_config
import json
import unittest

from app import utils
from app.gdoc import DocParser
from datetime import datetime
from fabfile import data
from render_utils import make_gdoc_context


class AppConfigTestCase(unittest.TestCase):
    """
    Testing dynamic conversion of Python app_config into Javascript.
    """
    def setUp(self):
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()

    def parse_data(self, response):
        """
        Trim leading variable declaration and load JSON data.
        """
        return json.loads(response.data[20:])

    def test_app_config_staging(self):
        response = self.client.get('/js/app_config.js')
        data = self.parse_data(response)
        self.assertEqual(data['DEBUG'], True)

    def test_app_config_production(self):
        app_config.configure_targets('production')
        response = self.client.get('/js/app_config.js')
        data = self.parse_data(response)
        app_config.configure_targets('test')
        self.assertFalse(data['DEBUG'])

    def test_app_config_no_db_credentials(self):
        from render_utils import flatten_app_config
        config = flatten_app_config()
        self.assertIsNone(config.get('database'))

    def test_date_filter(self):
        test_date = datetime(2016, 2, 1, 4, 0, 0)
        output = utils.ap_date_filter(test_date)
        self.assertEqual(output, 'Jan. 31, 2016')

    def test_time_filter(self):
        test_date = datetime(2016, 2, 1, 4, 0, 0)
        output = utils.ap_time_filter(test_date)
        self.assertEqual(output, '11:00')

    def test_time_filter_leading_zero(self):
        test_date = datetime(2016, 2, 1, 10, 0, 0)
        output = utils.ap_time_filter(test_date)
        self.assertEqual(output, '5:00')

    def test_time_period_filter(self):
        test_date = datetime(2016, 2, 1, 4, 0, 0)
        output = utils.ap_time_period_filter(test_date)
        self.assertEqual(output, 'p.m.')

    def test_zero_percent_filter(self):
        formatted = utils.percent_filter(0)
        self.assertEqual(formatted, '0%')

    def test_small_percent_filter(self):
        # 7927 is the number of precincts in Texas
        value = (1.0 / 7927.0) * 100
        formatted = utils.percent_filter(value)
        self.assertEqual(formatted, '<1%')

    def test_large_percent_filter(self):
        value = (7926.0 / 7927.0) * 100
        formatted = utils.percent_filter(value)
        self.assertEqual(formatted, '99.9%')

    def test_one_hundred_percent_filter(self):
        formatted = utils.percent_filter(100)
        self.assertEqual(formatted, '100%')

    def test_make_gdoc_context(self):
        with open('tests/data/testdoc.html') as f:
            html_string = f.read()

        doc = DocParser(html_string)
        context = make_gdoc_context(doc)
        self.assertEqual(doc, context['content'])

    def test_results_json(self):
        self.assertEqual(True, True)


class AppDelegatesTestCase(unittest.TestCase):
    def setUp(self):
        data.load_delegates()
        client = app.app.test_client()
        response = client.get('/data/delegates.json')
        self.delegates_data = json.loads(response.data)

    def test_has_national_data(self):
        self.assertTrue('nation' in self.delegates_data.keys())

    def test_expected_number_of_states(self):
        """
        60 states expected; 50 states, national, plus 8 territories and weird
        'US' catchall.
        """
        self.assertEqual(len(self.delegates_data.keys()), 60)

    def test_national_delegate_count(self):
        for candidate in self.delegates_data['nation']['dem']:
            if candidate['last'] == 'Sanders':
                delegates = candidate['delegates_count']
                break

        self.assertEqual(delegates, 168)

    def test_state_delegate_count(self):
        for candidate in self.delegates_data['IA']['dem']:
            if candidate['last'] == 'Clinton':
                delegates = candidate['superdelegates_count']
                break

        self.assertEqual(delegates, 3)

if __name__ == '__main__':
    unittest.main()
