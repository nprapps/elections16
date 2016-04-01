#!/usr/bin/env python

"""
Commands related to syncing copytext from Google Docs.
"""

import app_config

from fabric.api import task
from oauth.blueprint import get_document, get_spreadsheet


@task(default=True)
def update_copytext():
    """
    Downloads a Google Doc as an Excel file.
    """
    get_spreadsheet(app_config.COPY_GOOGLE_DOC_KEY,
                    app_config.COPY_PATH)


@task
def update_calendar():
    """
    Download calendar file.
    """
    get_spreadsheet(app_config.CALENDAR_GOOGLE_DOC_KEY,
                    app_config.CALENDAR_PATH)


@task
def update_docs():
    """
    Update Google docs.
    """
    for card_slug, gdoc_id in app_config.CARD_GOOGLE_DOC_KEYS.items():
        file_path = 'data/%s.html' % card_slug
        get_document(gdoc_id, file_path)
