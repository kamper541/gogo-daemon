#!/usr/bin/python

#-------------------------------------------------------------------------------
# Name          :  Cloud Data Logging
# Description   :  Storing sensor's value to Cloud
# Author        :  Marutpong Chailangka
# Created       :  2015-11-17
# Updated       :  2015-11-18
# Updated       :  2015-12-12
# Updated       :  2016-05-06
# Updated       :  2016-07-03
#-------------------------------------------------------------------------------
import threading
import queue
import time
import requests
import config
import os, sys
import json
from io import StringIO
import copy
import urllib
from urllib.request import urlopen
import consolelog

_rate_limit_cloud = 1 #seconds

APPLICATION_PATH   = os.path.abspath(os.path.dirname(sys.argv[0]))
QUEUE_FILE         = os.path.join(APPLICATION_PATH, "www", "media","log" , "logging_queue.txt")

LOG_TITLE           = "CloudData"

class CloudDataThread(threading.Thread):
    def __init__(self, gogod_config=None):
        threading.Thread.__init__(self)
        self.data_to_update = {}
        self.data_from_queue = {}
        self.last_handle = 0
        self.count = 0
        self.state_normal = False # False = queue, True = normal
        self.queue_not_upload = Queue()
        self.flag_connect = False

        self.conf = config.Config() if gogod_config is None else gogod_config

        self.api_key = self.conf.getClouddataKey()
        self._last_handle = {'field1':0}
        self.valid_names = ['field1','field2','field3','field4','field5','field6','field7','field8','created_at']
        consolelog.log(LOG_TITLE, "Created Thread")
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
        self.state_normal = False

        # Checking the exist queue first
        if self.count <= 1:

            if self.data_from_queue == {}:
                queue_data = self.get_queue_file()
                queue_data = self.check_valid_name(queue_data)
                if queue_data is not None and queue_data != {}:
                    self.data_from_queue = queue_data
                else:
                    self.pop_queue_file()
            else:
                self.state_normal = True

            if self.data_from_queue != {}:
                consolelog.log(LOG_TITLE, "Queueing")
                # if send data success then clear variable
                if self.updateData(self.data_from_queue):
                    self.data_from_queue = {}
                    self.pop_queue_file()

        if (self.count > 1 or  self.state_normal) and self.data_to_update != {} :
        #elif self.data_to_update != {} :
            self.count = 0
            if not self.updateData(self.data_to_update):
                self.onFail()
                self.addToQueue(self.data_to_update)

            self.clearData()

        elif self.data_to_update == {} :
            self.count = 0


        if self.count >= 4:
            self.count = 0

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
        dictData = self.check_valid_name(dictData)
        consolelog.log(LOG_TITLE, "%s" % dictData)
        self.getAPIKey()

        if not self.conf.validateClouddataKey(self.api_key):
            return False

        if dictData is None or dictData == {}:
            return True
        
        data = copy.deepcopy(dictData)
        data['key'] = self.api_key

        params = urllib.urlencode(dictData)
        request = urlopen("https://data.learninginventions.org/update?key=%s&%s" % (self.api_key, params) )
        try:
            # r = requests.post("https://data.learninginventions.org/update", data=data, ,verify=False)
            # return_data = r.text
            result = urlopen(request)
            return_data = result.read()
            self.last_timestamp = time.time()

            consolelog.log(LOG_TITLE, "Seq. =%s" % return_data)

            #self.flag_connect = False
            #return int(return_data) > -1
            return True

        except:
            consolelog.log(LOG_TITLE, "Connected Error")
            #self.flag_connect = False
            return False
        return False

    def check_valid_name(self, dictData=None):
        if dictData is None:
            return {}
        old_dict = dictData
        wanted_keys = self.valid_names
        new_dict = {k: old_dict[k] for k in set(wanted_keys) & set(old_dict.keys())}
        if len(new_dict) == 1 and 'created_at' in new_dict:
            return {}
        return new_dict

    def getDatetime(self):
        return time.strftime("%Y-%m-%d %H:%M:%S",time. gmtime())

    def onFail(self):
        if 'created_at' not in self.data_to_update:
            self.data_to_update['created_at'] = self.getDatetime()

    def addToQueue(self, record):
        #self.queue_not_upload.put(record)
        file = open(QUEUE_FILE, 'a')
        file.write("%s\r\n" % (json.dumps(record)))
        file.close()

    def pop_queue_file(self):
        return_data = None
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, 'r') as fin:
                data = fin.read().splitlines(True)
            if len(data) >0 :
                return_data = data[0]
                with open(QUEUE_FILE, 'w') as fout:
                    fout.writelines(data[1:])
        return return_data

    def add_to_firsttline_queue(self,record):
        with file(QUEUE_FILE, 'r') as original: data = original.read()
        with file(QUEUE_FILE, 'w') as modified: modified.write("%s\r\n" % (json.dumps(record)) + data)

    def get_queue_file(self):
        return_data = None
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, 'r') as f:
                data = f.readline()
                if data == '':
                    return return_data

                io_string = StringIO(data)
                try:
                    return json.load(io_string)
                except:
                    # if invalid
                    self.pop_queue_file()
                    consolelog.log(LOG_TITLE, "Queue file error")

        return return_data


    def checkQueue(self):


        '''

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
        '''
