#!/usr/bin/python

#-------------------------------------------------------------------------------
# Name          :  Cloud Data Logging
# Description   :  Storing sensor's value to the Cloud
# Author        :  Marutpong Chailangka
#-------------------------------------------------------------------------------
import threading
import time
import os, sys
import paho.mqtt.client as mqtt
import re
import random
import string

import config
import consolelog

_rate_limit_cloud = 1 #seconds

APPLICATION_PATH    = os.path.abspath(os.path.dirname(sys.argv[0]))
LOG_TITLE           = "CloudData2"

MQTT_ADDRESS    = 'broker.gogoboard.org'
MQTT_USER       = 'user'
MQTT_PASSWORD   = 'password'
MQTT_TOPIC      = 'log/+/+'  # [bme280|mijia]/[temperature|humidity|battery|status]
MQTT_CLIENT_ID  = ''

def mqtt_on_connect(client, userdata, flags, rc):
    client.is_connected = True
    client.is_connecting = False
    consolelog.log(LOG_TITLE, "Connected with result code %s" % str(rc))


def mqtt_on_disconnect(client, userdata, rc):
    client.is_connected = False
    client.is_connecting = False
    if rc != 0:
        consolelog.log(LOG_TITLE, "MQTT disconnected")

class CloudDataThread(threading.Thread):
    def __init__(self, gogod_config=None):
        threading.Thread.__init__(self)
        self.state_normal = False # False = queue, True = normal

        self.conf = config.Config() if gogod_config is None else gogod_config
        self._last_handle = {}

        self.data_to_update = {}

        self.uid = self.conf.get('datalog_uid')
        self.mqtt_client = None
        self.is_connected = False
        self.is_connecting = True

        global _rate_limit_cloud
        _rate_limit_cloud = _rate_limit_cloud - 0.05

        consolelog.log(LOG_TITLE, "Created Thread ")
        self.start()

    def run(self):
        global _rate_limit_cloud
        while (True):
            if len(self.data_to_update) > 0:
                for key in self.data_to_update:
                    if self.data_to_update[key]["is_public"]:
                        self.pub_publish(self.data_to_update[key])
                    else:
                        self.publish(self.data_to_update[key])

                self.data_to_update = {}

            if self.mqtt_client is not None:
                self.mqtt_client.loop(timeout=1.0, max_packets=1)
            
            time.sleep( _rate_limit_cloud )

    def processSetting(self, topic, value):
        if topic == 'setting/uid':
            self.setDatalogUid(value)

    def setDatalogUid(self, uid):
        self.uid = uid
        self.conf.save('datalog_uid', uid)
        self.init_mqtt_client()

    def getDatalogUid(self):
        self.uid = self.conf.get('datalog_uid')

    def prepareData(self, data_field, data_value):

        # if data_field not in self._last_handle or (time.time() - self._last_handle[data_field]) >= _rate_limit_cloud:
        if data_field not in self.data_to_update:
            # self._last_handle[data_field] = time.time()
            
            data_field = re.sub('[^a-zA-Z0-9\n\.]', '_', data_field.strip())

            data = {
                'user': self.uid,
                'is_public': False,
                'field': data_field,
                'value': data_value
            }
            self.data_to_update[data_field] = data
            # self.publish(data)
    
    def preparePubData(self, data_channel, data_field, data_value):

        # if data_field not in self._last_handle or (time.time() - self._last_handle[data_field]) >= _rate_limit_cloud:
        #     self._last_handle[data_field] = time.time()
        key = "%s/%s" % (data_channel, data_field)

        if key not in self.data_to_update:
            data_channel = re.sub('[^a-zA-Z0-9\n\.]', '_', data_channel.strip())
            data_field = re.sub('[^a-zA-Z0-9\n\.]', '_', data_field.strip())

            data = {
                'user': self.uid,
                'is_public': True,
                'channel': data_channel,
                'field': data_field,
                'value': data_value
            }
            self.data_to_update[key] = data

            # self.pub_publish(data)

    #Cover method prepareData
    def log(self, data_name, data_value):
        if self.uid is not None:
            self.prepareData(data_name, data_value)
    
    def pub_log(self, data_channel, data_name, data_value):
        # print data_channel, data_name, data_value
        self.preparePubData(data_channel, data_name, data_value)
        # if self.uid is not None:
        #     self.prepareData(data_name, data_value)

    def publish(self, data):

        if self.uid is None or self.uid == '':
            return

        if self.mqtt_client is None:
            self.init_mqtt_client()
        elif not self.mqtt_client.is_connected and not self.mqtt_client.is_connecting:
            self.init_mqtt_client()
        
        if self.mqtt_client.is_connected:
            consolelog.log(LOG_TITLE, data)
            self.mqtt_client.publish("log/%s/%s" % (data["user"], data["field"]), "%s %s=%s" % (data["user"], data["field"], data["value"]))

    def pub_publish(self, data):

        # uid = self.uid
        if self.uid is None or self.uid == '':
            # uid = data["channel"]
            self.uid = data["channel"] + self.random_string()

        if self.mqtt_client is None:
            self.init_mqtt_client()
        elif not self.mqtt_client.is_connected and not self.mqtt_client.is_connecting:
            self.init_mqtt_client()
        
        if self.mqtt_client.is_connected:
            consolelog.log(LOG_TITLE, data)
            self.mqtt_client.publish("plog/%s/%s" % (data["channel"], data["field"]), "%s %s=%s" % (data["channel"], data["field"], data["value"]))


    def init_mqtt_client(self):
        MQTT_USER = self.uid
        MQTT_CLIENT_ID = self.uid

        if (self.mqtt_client is not None and self.mqtt_client.is_connected):
            if self.mqtt_client.username != MQTT_USER:
                consolelog.log(LOG_TITLE, "MQTT disconnect the exists")
                self.mqtt_client.disconnect()
            else:
                consolelog.log(LOG_TITLE, "MQTT keep the exists")
                return

        self.mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
        self.mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        self.mqtt_client.on_connect = mqtt_on_connect
        self.mqtt_client.on_disconnect = mqtt_on_disconnect
        self.mqtt_client.is_connected = False
        self.mqtt_client.is_connecting = True
        self.mqtt_client.username = MQTT_USER

        # mqtt_client.on_message = on_message
        consolelog.log(LOG_TITLE, "MQTT connecting")

        self.mqtt_client.connect(MQTT_ADDRESS, port=1883, keepalive=10)
        time.sleep(1)
        # mqtt_client.loop_start()

    def random_string(self, stringLength=4):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))