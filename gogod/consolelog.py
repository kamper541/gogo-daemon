#!/usr/bin/python

#-------------------------------------------------------------------------------
# Name          :  Log to console
# Description   :
# Author        :  Marutpong Chailangka
#-------------------------------------------------------------------------------
import threading
import time
import os, sys
import copy

APPLICATION_PATH    = os.path.abspath(os.path.dirname(sys.argv[0]))

class ConsoleLog(threading.Thread):
    def __init__(self, gogod_config=None):
        threading.Thread.__init__(self)
        self.last_handle = 0
        # self.start()

    def run(self):
        print(None)

def log(title=None, text=None):
    print("%s, %10s : %s" % (getDateTime(), title, text))


def getDateTime():
    return time.strftime("%H:%M:%S", time.gmtime())
    # return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
