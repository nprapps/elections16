from time import time, sleep
from cement.core.foundation import CementApp
from random import random

LOOP_INTERVAL = 20

class NPRElexDaemon(CementApp):
    class Meta:
        label = 'nprelexdaemon'
        extensions = ['daemon']


with NPRElexDaemon() as app:
    app.daemonize()
    app.run()

    count = 0
    while True:
        start = time()

        count = count + 1
        for x in range(0, 90000000):
            random()

        end = time()

        wait = LOOP_INTERVAL - (end - start)

        print('Interval: %s' % count)
        print('Wait: %s' % wait)
        sleep(wait)
