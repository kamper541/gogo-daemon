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

flag_run = False

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
        print "PushBullet \t: background start"
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
        
        self.fetch_pushes()
        
        global flag_run
        if ((flag_run == False) and (self.token is not None)):
            print "PushBullet \t: starting"
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
        print "PushBullet \t: msg - >" + message
        message = json.loads(message)
        if (message['type'] == "tickle"):
            self.fetch_pushes(self.last_timestamp)
        self.getToken() #For check change token

    def on_error(self, ws, error):
        global flag_run
        flag_run = False
        self.set_status("error")
        print "PushBullet \t: WS Error"
        #print error

    def on_close(self, ws):
        global flag_run
        flag_run = False
        self.set_status("close")
        print "PushBullet \t: WS Closed"

    def on_open(self, ws):
        self.set_status("ok")
        print "PushBullet \t: WS Connected"

    def getToken(self):
        token =  self.conf.getPushbulletToken()
        # print token
        if ((self.token is not None) and (self.token != token)):
            print "PushBullet \t: Token changed by user"
            self.set_status("close")
            self.ws.close()
            self.stop()

        if ((self.token is None) and (len(token)==34)):
            self.token = token
            print "PushBullet \t: Changed token"

        elif(self.token is None):
            print "PushBullet \t: Invalid token file"

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
            print "PushBullet \t: Fetch Error"

if __name__ == "__main__":
    background = BackgroundCheck()
    time.sleep(60000)


