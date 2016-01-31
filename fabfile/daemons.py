#!/usr/bin/env python

from time import sleep, time
from fabric.api import execute, settings, task

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

    while True:
        now = time()

        if app_config.COPY_DEPLOY_INTERVAL and (now - copy_start) > app_config.COPY_DEPLOY_INTERVAL:
            copy_start = now
            logger.info('Update copy')
            execute('text.update')
            execute('render.copytext_js')

            logger.info('Update config')
            execute('render.app_config_js')

        if app_config.RESULTS_DEPLOY_INTERVAL and (now - results_start) > app_config.RESULTS_DEPLOY_INTERVAL:
            results_start = now
            logger.info('load results')
            execute('data.load_results')
            logger.info('deploy results')
            execute('deploy_results_cards')

        if app_config.CARD_DEPLOY_INTERVAL and (now - card_start) > app_config.CARD_DEPLOY_INTERVAL:
            card_start = now
            logger.info('deploy content cards')
            execute('deploy_all_cards')

        if app_config.SITE_ARCHIVE_INTERVAL and (now - archive_start) > app_config.SITE_ARCHIVE_INTERVAL:
            archive_start = now
            logger.info('archiving site')
            execute('archive_site')

        if run_once:
            logger.info('run once specified, exiting')
            sys.exit(0)

        sleep(1)
