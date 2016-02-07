#!/usr/bin/env python
import app_config
app_config.configure_targets('test')

from app import utils
from app.gdoc import DocParser
from datetime import datetime
from render_utils import make_gdoc_context

import app
import json
import unittest

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

        assert data['DEBUG'] == True

    def test_app_config_production(self):
        app_config.configure_targets('production')

        response = self.client.get('/js/app_config.js')

        data = self.parse_data(response)

        assert data['DEBUG'] == False

        app_config.configure_targets('staging')

    def test_app_config_no_db_credentials(self):
        from render_utils import flatten_app_config

        config = flatten_app_config()

        assert not config.get('database')

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

    def test_make_gdoc_context(self):
        with open('tests/data/testdoc.html') as f:
            html_string = f.read()

        doc = DocParser(html_string)
        context = make_gdoc_context(doc)
        self.assertEqual(doc, context['content'])

if __name__ == '__main__':
    unittest.main()
