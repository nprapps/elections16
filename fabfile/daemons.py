#!/usr/bin/env python

from time import sleep, time
from fabric.api import execute, task
from random import randint

import app_config
import render
import sys
import traceback


def slack_off():
    """
    Do a slow operation
    """
    sleep(randint(5, 15))


def safe_execute(*args, **kwargs):
    """
    Wrap execute() so that all exceptions are caught and logged.
    """
    try:
        execute(*args, **kwargs)
    except:
        print("ERROR [timestamp: %d]: Here's the traceback" % time())
        ex_type, ex, tb = sys.exc_info()
        traceback.print_tb(tb)
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

        print('results cycle hit')
        safe_execute('deploy_results_cards')
        # slack_off()
        card_end = time()
        print('results cycle finished in %ds' % (card_end - start))

        if modulo == 0:
            print('card cycle hit')
            safe_execute('deploy_all_cards')
            # slack_off()
            print('card cycle finished in %ds' % (time() - card_end))

        duration = time() - start
        wait = app_config.RESULTS_DEPLOY_INTERVAL - duration

        print('Deploying cards ran in %ds (cumulative)' % duration)

        if wait < 0:
            print('WARN: Deploying cards took %ds longer than %ds' % (abs(wait), app_config.RESULTS_DEPLOY_INTERVAL))
            wait = 0

        if run_once:
            print 'Run once specified, exiting.'
            sys.exit()
        else:
            sleep(wait)
