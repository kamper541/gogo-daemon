#!/usr/bin/python

#-------------------------------------------------------------------------------
# Name          :  Background Worker for fetching push from Push Bullet
# Description   :  Connecting websocket to pushbullet, On websocket changed then HTTP api to fetch the pushes
#                  and sense for failure networking and changing configuration file
# Author        :  Marutpong Chailangka
# Created       :  2015-04-24
# Updated       :  2015-07-18
# Updated       :  2016-03-16
#-------------------------------------------------------------------------------

import websocket
import thread
import threading
import time
import json
import urllib2, base64
import os
import config
import consolelog

flag_run = False
LOG_TITLE           = "PushBullet"

class BackgroundCheck(object):
    """ Threading example class

    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, setKeyValueEvent):
        """ Constructor

        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = 60
        self.callback_setKeyValueEvent = setKeyValueEvent
        self.status = "none"
        self.pushbullet = None

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        """ Method that runs forever """
        consolelog.log(LOG_TITLE, "background started")
        while True:
            # Do something
            # print('Status : ' + self.status)
            if (self.status=="none"):
                self.new_ws_connection()
            elif (self.status == "close"):
                self.new_ws_connection()

            time.sleep(self.interval)

    def new_ws_connection(self):
        self.pushbullet = PushBullet(self.set_status, self.callback_setKeyValueEvent)
        self.pushbullet.start()

    def set_status(self, status):
        self.status = status


class PushBullet(threading.Thread):
    def __init__(self, set_status, setKeyValueEvent):
        threading.Thread.__init__(self, name="PushBullet")
        super(PushBullet, self).__init__()
        self._stop = threading.Event()
        self.callback_setKeyValueEvent = setKeyValueEvent
        self.set_status = set_status
        self.token = None
        self.last_timestamp = time.time()

        self.conf = config.Config()

    def stop(self):
        self._stop.set()

    def run(self):
        # self.token = "m3b2ydsSGqkq9meRZAgbKoE0PmSXQqAB"
        
        self.getToken()

        if self.is_valid_token(self.token):
            self.fetch_pushes()
        
        global flag_run
        if ((flag_run == False) and (self.token is not None)):
            consolelog.log(LOG_TITLE, "starting")
            self.connect()

    def connect(self):
        global flag_run
        flag_run = True
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp("wss://stream.pushbullet.com/websocket/%s" % self.token,
                                on_message = self.on_message,
                                on_error = self.on_error,
                                on_close = self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()

    def on_message(self, ws, message):
        self.set_status("ok")
        consolelog.log(LOG_TITLE, "msg - > %s" % message)
        message = json.loads(message)
        if (message['type'] == "tickle"):
            self.fetch_pushes(self.last_timestamp)
        self.getToken() #For check change token

    def on_error(self, ws, error):
        global flag_run
        flag_run = False
        self.set_status("error")
        consolelog.log(LOG_TITLE, "WS Error")
        #print error

    def on_close(self, ws):
        global flag_run
        flag_run = False
        self.set_status("close")
        consolelog.log(LOG_TITLE, "WS Closed")

    def on_open(self, ws):
        self.set_status("ok")
        consolelog.log(LOG_TITLE, "WS Connected")

    def getToken(self):
        token =  self.conf.getPushbulletToken()
        # print token
        if ((self.token is not None) and (self.token != token)):
            consolelog.log(LOG_TITLE, "Token changed by user")
            self.set_status("close")
            self.ws.close()
            self.stop()

        if ((self.token != token) and self.is_valid_token(token) ):
            self.token = token
            consolelog.log(LOG_TITLE, "Changed token")

        elif((self.token != token) and self.token is not None and not self.is_valid_token(token)):
            consolelog.log(LOG_TITLE, "Invalid token file")

    def is_valid_token(self, token=None):
        if token is None:
            return False
        return (len(token)==34)

    def fetch_pushes(self, timestamp=1429750800):
        request = urllib2.Request("https://api.pushbullet.com/v2/pushes?modified_after=%s" % timestamp)
        request.add_header("Authorization", "Bearer %s" % self.token)
        try:
            result = urllib2.urlopen(request)
            json_data = result.read()
            self.last_timestamp = time.time()
            data = json.loads(json_data)
            #print data
            if 'pushes' in data:
                for entry in data['pushes']:
                    if (not entry['dismissed']):
                        if (len(entry['title'].split(' '))==1):
                            self.callback_setKeyValueEvent(entry['title'],entry['body'])
                        # print data
        except:
            consolelog.log(LOG_TITLE, "Fetch Error")

if __name__ == "__main__":
    background = BackgroundCheck()
    time.sleep(60000)


