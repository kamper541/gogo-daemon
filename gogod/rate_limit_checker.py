#!/usr/bin/python

#-------------------------------------------------------------------------------
# Name          :  Rate Limit Checker
# Author        :  Marutpong Chailangka
#-------------------------------------------------------------------------------

import time
import os, sys
APPLICATION_PATH    = os.path.abspath(os.path.dirname(sys.argv[0]))

class RateLimitChecker():
    def __init__(self, limit_secs=0.25):
        self.last_handle_time   = 0
        self.limit_secs         = limit_secs
        self.dict_data           = {}

    def is_passed_limit(self, name='default'):
        if name in self.dict_data and (time.time() - self.dict_data[name]) < self.limit_secs:
            return False
        self.dict_data[name] = time.time()
        return True
