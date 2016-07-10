#!/usr/bin/python

#-------------------------------------------------------------------------------
# Name          :  IFTTT Trigger https://ifttt.com/maker
# Description   :  Making a web request to IFTTT Maker Channel as a trigger
# Author        :  Marutpong Chailangka
#-------------------------------------------------------------------------------
import threading
import time
import requests
import config
import os, sys

import consolelog

_rate_limit_ifttt   = 0.25 #seconds
APPLICATION_PATH    = os.path.abspath(os.path.dirname(sys.argv[0]))
LOG_TITLE           = "IFTTT"

class IftttTrigger():
    def __init__(self, gogod_config=None):
        self.last_handle_time   = 0
        self.conf               = config.Config() if gogod_config is None else gogod_config
        self.api_key            = self.conf.get_iftt_key()
        self.event_name         = None
        self.dict_data           = None
        consolelog.log(LOG_TITLE, "Created Class")

    def getAPIKey(self):
        self.api_key = self.conf.get_iftt_key()

    def trigger(self, cmd):

        if len(cmd) < 3 :
            return False

        if (time.time() - self.last_handle_time) <  _rate_limit_ifttt:
            #Flush if it's very high frequency
            return False
        self.last_handle_time = time.time()
        event_name = cmd[1]
        dict_data = {}

        for i, name in enumerate(cmd):
            value_index = i-1
            if value_index > 0:
                dict_data["value%s" % value_index] = cmd[i]

        self.event_name = event_name
        self.dict_data = dict_data

        thread_request = threading.Thread(target=self.makeWebRequest, args=(self.event_name,self.dict_data,))
        thread_request.start()

    def makeWebRequest(self,event_name =None, dict_data=None):

        self.getAPIKey()
        if event_name is None or self.api_key is None:
            return False
        #self.flag_connect = True

        consolelog.log(LOG_TITLE, event_name)
        consolelog.log(LOG_TITLE, dict_data)

        url = "https://maker.ifttt.com/trigger/%s/with/key/%s" % (event_name, self.api_key)
        try:
            r = requests.post(url, data=dict_data)
            return_data = r.text
            self.last_handle_time = time.time()
            consolelog.log(LOG_TITLE, return_data)
            #self.flag_connect = False
            return True

        except:
            consolelog.log(LOG_TITLE, "Connected Error")
            #self.flag_connect = False
            return False
        return False

    def clearData(self):
        self.event_name = None
        self.dict_data = None

if __name__ == "__main__":
    app = IftttTrigger()
    app.makeWebRequest('notify',{'value1':'test'})