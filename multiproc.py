#! /usr/bin/env python3

import multiprocessing as mp
import traceback
import time
import sys
import signal

class Forever(mp.Process):
    class mpGraceExit(Exception): pass

    def __init__(self):
        super().__init__()

    def handle(self, sig, stack):
        print('Child Process: Handling ')
        raise self.mpGraceExit()

    def cleanup(self):
        """Anything needs to be done to cleanup"""
        print('Child Process: cleanup ***')

    def run(self):
        """Wrapper so that it can handle graceful exit and cleanup"""

        """
        installing sig handler:
         1. can't be in __init__()
         2. run()be is a good place to put
         3. or has to be after process already started
            so that handler is in its process, and not visible to parent process
        thus, this class is selfcontained

        NOTE: IF handler installed before process started,
        it will override parent process' sig handler
        """
        signal.signal(signal.SIGTERM, self.handle)

        print('mp Started')
        try:
            self.run_actual()
        except (KeyboardInterrupt, Exception, self.mpGraceExit) as e:
            print('Child Process: EXCEPTION!!! Cleaning up')
            self.cleanup()
            print('\nmp ended')

    def run_actual(self):
        """Put actual run here, it can take a long time to run and doesn't matter"""

        while True:
            time.sleep(5)
            sys.stdout.write('.')
            sys.stdout.flush()



class GracefulExit(Exception):
   pass

def signal_handler(signum, frame):
    print('MainThread Handling')
    raise GracefulExit()

signal.signal(signal.SIGTERM, signal_handler)
myf = Forever()
try:
    time.sleep(5)
    myf.start()
    print('Main Started')
    #myf.join()
    time.sleep(5)
    print('Terminating')
    myf.terminate()
    print('exitcode:', myf.exitcode)
    time.sleep(2)
    print('Terminating again')
    myf.terminate()
except Exception as e:
    print('Main thread exception. Terminating')
    myf.terminate()
finally:

    myf.join()
    print('exitcode:', myf.exitcode)
    print('Main Ended')
