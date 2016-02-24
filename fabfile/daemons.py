#!/usr/bin/env python

from time import sleep, time
from fabric.api import execute, require, settings, task
from fabric.state import env


import app_config
import logging
import sys

logging.basicConfig(format=app_config.LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(app_config.LOG_LEVEL)


@task
def deploy(run_once=False):
    """
    Harvest data and deploy cards
    """
    require('settings', provided_by=['production', 'staging'])
    try:
        with settings(warn_only=True):
            main(run_once)
    except KeyboardInterrupt:
        sys.exit(0)


def main(run_once=False):
    """
    Main loop
    """
    copy_start = 0
    results_start = 0
    card_start = 0
    archive_start = 0
    delegates_start = 0

    while True:
        now = time()

        if app_config.COPY_DEPLOY_INTERVAL and (now - copy_start) > app_config.COPY_DEPLOY_INTERVAL:
            copy_start = now
            logger.info('Update copy')
            execute('text.update')

        if app_config.RESULTS_DEPLOY_INTERVAL and (now - results_start) > app_config.RESULTS_DEPLOY_INTERVAL:
            results_start = now
            logger.info('load results')
            execute('data.load_results')

        if app_config.DELEGATES_DEPLOY_INTERVAL and (now - delegates_start) > app_config.DELEGATES_DEPLOY_INTERVAL:
            sleep(5)
            delegates_start = now
            logger.info('load delegates')
            execute('data.load_delegates')
            sleep(5)

        if app_config.CARD_DEPLOY_INTERVAL and (now - card_start) > app_config.CARD_DEPLOY_INTERVAL:
            card_start = now
            logger.info('deploy content cards')
            execute('deploy_cards')

        if env.settings == 'production' and app_config.SITE_ARCHIVE_INTERVAL and (now - archive_start) > app_config.SITE_ARCHIVE_INTERVAL:
            archive_start = now
            logger.info('archiving site')
            execute('archive_site')

        if run_once:
            logger.info('run once specified, exiting')
            sys.exit(0)

        sleep(1)
