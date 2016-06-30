#!/usr/bin/python

#-------------------------------------------------------------------------------
# Name          :  Cloud Data Logging
# Description   :  Storing sensor's value to Cloud
# Author        :  Marutpong Chailangka
# Created       :  2015-11-17
# Updated       :  2015-11-18
# Updated       :  2015-12-12
# Updated       :  2016-05-06
#-------------------------------------------------------------------------------
import datetime
import threading
import Queue
import time
import urllib
import urllib2, base64
import os
import config

_rate_limit_cloud = 1 #seconds

class CloudDataThread(threading.Thread):
    def __init__(self, gogod_config=None):
        threading.Thread.__init__(self)
        self.data_to_update = {}
        self.data_from_queue = {}
        self.last_handle = 0
        self.count = 0
        self.queue_not_upload = Queue.Queue()
        self.flag_connect = False

        self.conf = config.Config() if gogod_config is None else gogod_config

        self.api_key = self.conf.getClouddataKey()
        self._last_handle = {'field1':0}
        print "CloudData \t: Created Thread"
        self.start()


    def run(self):
        global _rate_limit_cloud
        _rate_limit_cloud = _rate_limit_cloud - 0.05
        self.checkdo()
        # while (True):
        #    if (time.time() - self.last_handle) >= _rate_limit_cloud:
                
                
        #        self.last_handle = time.time()
        #    time.sleep( 0.05 )

    def checkdo(self):
        threading.Timer(1.0, self.checkdo).start()
        self.count += 1

        if self.count <= 1 :
            self.checkQueue()

        elif self.data_to_update != {} :
            self.count = 0
            if not self.updateData(self.data_to_update):
                self.onFail()
                self.addToQueue(self.data_to_update)

            self.clearData()

    def getAPIKey(self):
        self.api_key = self.conf.getClouddataKey()

    def prepareData(self, data_name, data_value):

        # if data_name not in self._last_handle or (time.time() - self._last_handle[data_name]) >= _rate_limit:
        #     self._last_handle[name] = time.time()
            
        if data_name not in self.data_to_update:
            self.data_to_update[data_name] = data_value

    #Cover method prepareData
    def log(self, data_name, data_value):
        self.prepareData(data_name, data_value)

    def clearData(self):
        self.data_to_update = {}

    def updateData(self, dictData):
        #if self.flag_connect:
        #    return False

        #self.flag_connect = True
        self.getAPIKey()
        params = urllib.urlencode(dictData)

        print "CloudData \t: %s" % params

        request = urllib2.Request("https://data.learninginventions.org/update?key=%s&%s" % (self.api_key, params) )
        try:
            result = urllib2.urlopen(request)
            json_data = result.read()
            self.last_timestamp = time.time()
            print "CloudData \t: Seq. =%s" % json_data

            #self.flag_connect = False
            return int(json_data) > 0

        except:
            print "CloudData \t: Connected Error"
            #self.flag_connect = False
            return False
        return False

    def getDatetime(self):
        return time.strftime("%Y-%m-%d %H:%M:%S",time. gmtime())

    def onFail(self):
        if 'created_at' not in self.data_to_update:
            self.data_to_update['created_at'] = self.getDatetime()

    def addToQueue(self, record):
        self.queue_not_upload.put(record)

    def checkQueue(self):
        if len(self.data_from_queue)>0:
            if self.updateData(self.data_from_queue):
                print "queue"
                print self.data_from_queue
                self.data_from_queue = {}
        elif not self.queue_not_upload.empty():
            self.data_from_queue = self.queue_not_upload.get()
            print self.data_from_queue
            if self.updateData(self.data_from_queue):
                self.data_from_queue = {}


