#!/usr/bin/env python
"""
Commands related to syncing docs and spreadsheets from Google Drive.
"""

import app_config
import copytext

from fabric.api import task
from fabric.state import env
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
def update_active_docs():
    """
    Update active Google docs.
    """
    COPY = copytext.Copy(app_config.COPY_PATH)
    if hasattr(env, 'settings') and env.settings == 'production':
        state = COPY['meta']['prod_state']['value']
    elif hasattr(env, 'settings') and env.settings == 'staging':
        state = COPY['meta']['stage_state']['value']
    else:
        state = COPY['meta']['dev_state']['value']

    script = COPY[state]

    for row in script:
        if row['function'] == 'live_audio':
            gdoc_id = 'live_coverage_active'
        else:
            gdoc_id = app_config.CARD_GOOGLE_DOC_KEYS.get(row['function'], None)

        if gdoc_id:
            file_path = 'data/%s.html' % row['function']
            get_document(gdoc_id, file_path)


@task
def update_all_docs():
    """
    Update Google docs.
    """
    for card_slug, gdoc_id in app_config.CARD_GOOGLE_DOC_KEYS.items():
        file_path = 'data/%s.html' % card_slug
        get_document(gdoc_id, file_path)
