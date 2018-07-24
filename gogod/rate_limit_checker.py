#!/usr/bin/python

#-------------------------------------------------------------------------------
# Name          :  Rate Limit Checker
# Author        :  Marutpong Chailangka
#-------------------------------------------------------------------------------

import time
import os, sys
APPLICATION_PATH    = os.path.abspath(os.path.dirname(sys.argv[0]))

class RateLimitChecker:
    def __init__(self, limit_secs=0.25):
        self.last_handle_time   = time.time()
        self.limit_secs         = limit_secs
        self.dict_data           = {}

    def is_passed_limit(self, name='default'):
        return self.is_passed_custom(name, self.limit_secs)

    def is_passed_custom(self, name='default', rate=0.25):
        if name not in self.dict_data:
            self.dict_data[name] = time.time()
            return True

        time.sleep(0.001)
        if (time.time() - self.dict_data[name]) > self.limit_secs:
            self.dict_data[name] = time.time()
            return True
        return False

    def is_passed(self):
        time.sleep(0.001)
        if (time.time() - self.last_handle_time) > self.limit_secs:
            self.last_handle_time = time.time()
            return True
        return False
