from time import time, sleep
from cement.core.foundation import CementApp
from random import random

LOOP_INTERVAL = 20
SLOW_LOOP_INTERVAL = 60
SLOW_LOOP_MODULO = SLOW_LOOP_INTERVAL / LOOP_INTERVAL


class ElectionResultsDaemon(CementApp):
    class Meta:
        label = 'nprelexdaemon'
        extensions = ['daemon']

    def slack_off(self):
        for x in range(0, 20000000):
            random()


with ElectionResultsDaemon() as app:
    app.daemonize()
    app.run()

    count = 0
    while True:
        start = time()

        modulo = count % SLOW_LOOP_MODULO

        if modulo == 0:
            app.slack_off()
            app.log.info('Per minute cycle hit (publish all content)')

        app.log.info('20 second cycle hit (publish results)')
        app.slack_off()

        end = time()
        wait = LOOP_INTERVAL - (end - start)

        count = count + 1

        if wait > 0:
            sleep(wait)



