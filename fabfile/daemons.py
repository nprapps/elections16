#!/usr/bin/env python

from time import sleep, time
from fabric.api import execute, task

import app_config
import logging
import sys
import traceback

logging.basicConfig(format=app_config.LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(app_config.LOG_LEVEL)

def safe_execute(*args, **kwargs):
    """
    Wrap execute() so that all exceptions are caught and logged.
    """
    try:
        timestamp = time()
        execute(*args, **kwargs)
    except:
        ex_type, ex, tb = sys.exc_info()
        logger.error("ERROR [timestamp: {0}] - {1} | Traceback".format(timestamp, ex))
        logger.debug(traceback.format_tb(tb))
        del tb


@task
def deploy(run_once=False):
    """
    Harvest data and deploy cards
    """
    count = 0

    while True:
        start = time()

        modulo = count % (app_config.CARD_DEPLOY_INTERVAL / app_config.RESULTS_DEPLOY_INTERVAL)

        logger.info('Update copy')
        safe_execute('text.update')
        safe_execute('render.copytext_js')
        logger.info('Update config')
        safe_execute('render.app_config_js')
        logger.info('load results')
        safe_execute('data.load_results')
        logger.info('deploy results')
        safe_execute('deploy_results_cards')
        results_end = time()
        logger.info('deploying results finished in %ds' % (results_end - start))

        wait = app_config.RESULTS_DEPLOY_INTERVAL - (results_end - start)

        if modulo == 0:
            logger.info('deploy content cards')
            safe_execute('deploy_all_cards')
            card_end = time()
            card_duration = card_end - results_end
            next_card_time = app_config.CARD_DEPLOY_INTERVAL - (card_end - start)
            logger.info('deploying content cards finished in %ds' % (card_duration))
            logger.info('WAITING %ds till next content deployment' % next_card_time)

        total_duration = time() - start
        cumulative_wait = app_config.RESULTS_DEPLOY_INTERVAL - total_duration

        count = count + 1

        logger.info('Deploying cards ran in %ds (cumulative)' % total_duration)

        if cumulative_wait < 0:
            logger.info('WARN: Deploying all cards took %ds longer than %ds' % (abs(wait), app_config.RESULTS_DEPLOY_INTERVAL))
            wait = 0

        if run_once:
            logger.info('Run once specified, exiting.')
            sys.exit()
        else:
            logger.info('WAITING %ds till next results deployment' % wait)
            sleep(wait)
