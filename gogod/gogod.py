#!/usr/bin/env python

import serial
import pistat  # Raspbery Pi Info
import camera
import ip
import audio
import RPi.GPIO as GPIO
import tornado.ioloop, tornado.web, tornado.websocket, tornado.httpclient
import os, uuid, time, threading
import os.path
import sys
import wireless
import rpi_system
import loggerfile
import loggercloud
import logging
import mail
from mail import EmailParam
import const
import sms
import rfid
import text2speech
import urllib2
import push
import config
import subprocess
from threading import Thread
import json, string
from addons import Addons
import addons_function
import webui_function

# logging.basicConfig(
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#         level=logging.CRITICAL)
APPLICATION_PATH = os.path.abspath(os.path.dirname(sys.argv[0]))
WWW_PATH = os.path.join(APPLICATION_PATH, "www")
MEDIA_PATH = os.path.join(APPLICATION_PATH, "www", "media")


class GogoD():
    def __init__(self):

        self.camera_status = 0
        self.perform_face_detection = 0
        self.face_found = 0

        self.TX_BUFFER = [0] * const.TX_REGISTER_SIZE
        self.TX_BUFFER[const.REG_PACKET_TYPE] = 2  # this is the packet type ID

        print "Application Path = %s" % APPLICATION_PATH

        print "Serial monitor started"
        self.ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=0)

        self.pistat = pistat.PiStats()
        self.camera = camera.CameraControl()

        self.conf = config.Config()

        # init with log and media paths
        self.data_logger = loggerfile.dataLogger(os.path.join(MEDIA_PATH, "log"), MEDIA_PATH)
        self.cloud_logger = loggercloud.CloudDataThread(self.conf)

        self.background_push = push.BackgroundCheck(self.setKeyValueEvent)
        self.text2speech = text2speech.TextToSpeech()
        self.webUIfunc = webui_function.WebUIFunction()
        self.addons_mng = addons_function.AddOnsManager()

        # Addons
        self.addons_thread = Addons(APPLICATION_PATH, self.setKeyValueEvent)
        self.addons_thread.start()

        # Pi Display : current image
        self.current_show_image = "pet_idle.png"
        # Auto connect to wifi
        wireless.autoconnect(self.wifi_status_callback)

        thread_php = Thread(target=os.system, args=(r"php -S 0.0.0.0:8889 -t %s" % (WWW_PATH),))
        thread_php.start()
        # subprocess.Popen(r"php -S 0.0.0.0:8889 -t %s" % (APPLICATION_PATH+"/www/") ,shell=True)
        # os.system(r"php -S 0.0.0.0:8889 -t %s" % (APPLICATION_PATH+"/www/") )

    def send_buffer(self, TX_BUFFER):
        checksum = sum(TX_BUFFER) & 0xff
        outputBuffer = [const.TX_HEADER1, const.TX_HEADER2] + TX_BUFFER
        outputBuffer.append(checksum)

        '''if TX_BUFFER[0] == const.REG_PACKET_TYPE_KEY_VALUE:
            print "==================================================="
            print outputBuffer'''
        outputString = ''.join(chr(c) for c in outputBuffer)
        self.ser.write(outputString)

    def send_on_keyvalue_buffer(self, packet_type, data):
        pre_output_buffer = [packet_type, len(data) + 3] + data + [0]
        if len(pre_output_buffer) > const.TX_REGISTER_SIZE:
            pre_output_buffer = pre_output_buffer[0:const.TX_REGISTER_SIZE - 1] + [0]
        # print pre_output_buffer
        self.send_buffer(pre_output_buffer)
        # TX_BUFFER = pre_output_buffer
        # checksum = sum(TX_BUFFER) & 0xff
        # outputBuffer = [const.TX_HEADER1, const.TX_HEADER2] + TX_BUFFER
        # outputBuffer.append(checksum)
        # print outputBuffer
        # outputString = ''.join(chr(c) for c in outputBuffer)
        # self.ser.write(outputString)

    def wifi_status_callback(self, status):
        self.TX_BUFFER[const.REG_WIFI_STATUS] = status

    def mail_status_callback(self, status):
        self.TX_BUFFER[const.REG_MAIL_STATUS] = status

    def sms_status_callback(self, status):
        self.TX_BUFFER[const.REG_SMS_STATUS] = status

    def rfid_status_callback(self, status):
        self.TX_BUFFER[const.REG_RFID_STATUS] = status

    def rfid_read_tag_callback(self, value):
        self.TX_BUFFER[const.REG_RFID_TAG_CONTENT] = value

    def setTapEvent(self, xpos, ypos):

        print "Tap event at (%s, %s)" % (xpos, ypos)
        xpos = int(xpos)
        ypos = int(ypos)

        self.TX_BUFFER[const.REG_SCREEN_TAP] = 1
        self.TX_BUFFER[const.REG_SCREEN_TAP_X_POS_HB] = xpos >> 8
        self.TX_BUFFER[const.REG_SCREEN_TAP_X_POS_LB] = xpos & 0xff
        self.TX_BUFFER[const.REG_SCREEN_TAP_Y_POS_HB] = ypos >> 8
        self.TX_BUFFER[const.REG_SCREEN_TAP_Y_POS_LB] = ypos & 0xff

        event_array = []
        event_array.append(xpos >> 8)
        event_array.append(xpos & 0xff)
        event_array.append(ypos >> 8)
        event_array.append(ypos & 0xff)
        self.send_on_keyvalue_buffer(const.REG_PACKET_TYPE_ON_TAP, event_array)

    def setKeyValueEvent(self, key, value):
        key = key.strip()
        value = value.strip()
        parameter = key + "," + value
        parameter = parameter.lower()
        print "Event key,vale  = '%s'" % (parameter)
        event_array = [ord(c) for c in parameter]

        if value != "":
            if key == "speech":
                self.broadcast_websocket("speech," + value)
            t = Thread(target=self.setKeyValueEvent, args=(key, "",))
            t.start()
        else:
            time.sleep(0.5)

        self.send_on_keyvalue_buffer(const.REG_PACKET_TYPE_KEY_VALUE, event_array)

    def broadcast_websocket(self, message):
        for client in ws_clients:
            client.write_message(message)

    def broadcast_to_interface(self, key, value):
        for client in ws_addons_clients:
            client.write_message("%s,%s" % (key, value))

    def update(self):

        # =============================================
        self.TX_BUFFER[const.REG_CAMERA_FLAGS] = 0
        if self.camera.find_face_is_on():
            if self.camera.face_found():
                self.TX_BUFFER[const.REG_CAMERA_FLAGS] |= 1 << 2
                print "Found a face"

        # =============================================
        # update Raspberry Pi revision
        try:
            rPiRevision = GPIO.RPI_REVISION
        except:
            rPiRevision = 0
            pass
        self.TX_BUFFER[const.REG_HW_VERSION] = rPiRevision

        # =============================================
        # Update CPU Info
        self.pistat.update_stats()
        cpu_info = self.pistat.get_cpu_info()
        mem_info = self.pistat.get_memory_info()

        self.TX_BUFFER[const.REG_CPU_LOAD] = int(cpu_info['percent'])
        self.TX_BUFFER[const.REG_CPU_TEMP] = int(self.pistat.temp_in_celsius)
        self.TX_BUFFER[const.REG_MEM_USED] = int(mem_info['percent'])

        # print "CPU %i%%" % cpu_info['percent']
        # print "MEM %i%%" % mem_info['percent']

        # =============================================
        ip_list = ip.get_ip_list('eth0')
        if ip_list is not None:
            # print "LAN = %s" % ip_list
            self.TX_BUFFER[const.REG_IP_1] = int(ip_list[0])
            self.TX_BUFFER[const.REG_IP_2] = int(ip_list[1])
            self.TX_BUFFER[const.REG_IP_3] = int(ip_list[2])
            self.TX_BUFFER[const.REG_IP_4] = int(ip_list[3])
        else:
            self.TX_BUFFER[const.REG_IP_1] = 0
            self.TX_BUFFER[const.REG_IP_2] = 0
            self.TX_BUFFER[const.REG_IP_3] = 0
            self.TX_BUFFER[const.REG_IP_4] = 0

        # =============================================
        ip_list = ip.get_ip_list('wlan0')
        if ip_list is not None:
            # print "WLAN = %s" % ip_list
            self.TX_BUFFER[const.REG_WLAN_IP_1] = int(ip_list[0])
            self.TX_BUFFER[const.REG_WLAN_IP_2] = int(ip_list[1])
            self.TX_BUFFER[const.REG_WLAN_IP_3] = int(ip_list[2])
            self.TX_BUFFER[const.REG_WLAN_IP_4] = int(ip_list[3])
        else:
            # print "NO WLAN IP"
            self.TX_BUFFER[const.REG_WLAN_IP_1] = 0
            self.TX_BUFFER[const.REG_WLAN_IP_2] = 0
            self.TX_BUFFER[const.REG_WLAN_IP_3] = 0
            self.TX_BUFFER[const.REG_WLAN_IP_4] = 0

        # =============================================
        self.TX_BUFFER[const.REG_CAMERA_FLAGS] = self.TX_BUFFER[const.REG_CAMERA_FLAGS] | self.camera.camera_is_on() | (
        self.camera.find_face_is_on() << 1)

        while True:

            text_cmd = self.ser.readline().rstrip()
            if len(text_cmd) == 0:
                break

            if len(text_cmd) < 2:
                print "cmd is too short"
                break

            if ord(text_cmd[0]) != 5:
                # print "cmd header is wrong"
                # print ord(text_cmd[0])
                break

            cmd = [ord(c) for c in text_cmd]
            # print "cmd is %s " % cmd

            if cmd[1] == const.USE_CAMERA:
                self.camera.use_camera()
                if self.camera.camera_is_on():
                    print "Camera is on"
                else:
                    print "Camera cannot be turned on"

            elif cmd[1] == const.CLOSE_CAMERA:
                self.camera.close_camera()
                if not self.camera.camera_is_on():
                    print "Camera is off"
                else:
                    print "Cannot turn off camera"

            elif cmd[1] == const.START_FIND_FACE:
                self.camera.start_find_face()
                if self.camera.find_face_is_on():
                    print "Find Face is ON"
                else:
                    print "Cannot start Find Face"

            elif cmd[1] == const.STOP_FIND_FACE:
                self.camera.stop_find_face()
                if not self.camera.find_face_is_on():
                    print "Find Face is OFF"
                else:
                    print "Cannot turn off find face"

            elif cmd[1] == const.TAKE_SNAP_SHOT:
                self.camera.take_snapshot()
                print "Snap shot taken"

            elif cmd[1] == const.TAKE_PREVIEW_IMAGE:
                self.camera.take_preview_image()
                print "preview shot taken"

            elif cmd[1] == const.SEND_MAIL:
                arg = ''.join(chr(i) for i in cmd[2:]).split(',')
                param = EmailParam()
                param.recipient = arg[0]
                param.subject = arg[1]
                param.body = arg[2]
                print "Email : send to %s" % (param.recipient)
                mail.send(self.mail_status_callback, param)

            elif cmd[1] == const.PLAY_SOUND:
                # [::-1] reverses the character order in the string
                file_name = cmd[2:]
                # convert list of ascii values to string
                file_name = ''.join(chr(i) for i in file_name)
                listsoundfiletype = ['mp3', 'ogg']
                listsoundfiletypedirectory = ['audio/mpeg', 'audio/ogg']
                for index, type in enumerate(listsoundfiletype):
                    file_name_check = file_name + "." + type
                    if os.path.exists(os.path.join(MEDIA_PATH, file_name_check)):
                        file_name = file_name_check
                        break
                    elif os.path.exists(os.path.join(MEDIA_PATH, recordings, file_name_check)):
                        file_name = file_name_check
                        break
                print "Play sound %s" % file_name
                self.broadcast_websocket("play_sound," + file_name)
                if os.path.exists(os.path.join(MEDIA_PATH, file_name)):
                    audio.play_sound(os.path.join(MEDIA_PATH, file_name))
                else:
                    audio.play_sound(os.path.join(MEDIA_PATH, recordings, file_name_check))

            elif cmd[1] == const.STOP_SOUND:
                print "Stop sound"
                audio.stop_sound()

            elif cmd[1] == const.SHOW_IMAGE:
                image_filename = ''.join(chr(i) for i in cmd[2:])
                print "show image %s" % image_filename
                listimagefiletype = ['png', 'jpg', 'jpeg', 'bmp', 'PNG']
                for type in listimagefiletype:
                    image_filename2 = image_filename + "." + type
                    if os.path.exists(os.path.join(MEDIA_PATH, image_filename2)):
                        image_filename = image_filename2
                        break
                    elif os.path.exists(os.path.join(MEDIA_PATH, "snapshots", image_filename2)):
                        image_filename = 'snapshots/' + image_filename2
                        break
                self.current_show_image = image_filename
                self.broadcast_websocket("set_image," + image_filename)


            elif cmd[1] == const.WIFI_CONNECT:
                ssid, password = ''.join(chr(i) for i in cmd[2:]).split(',')

                if password == '':
                    password = None

                wireless.connect(self.wifi_status_callback, ssid, password)

            elif cmd[1] == const.WIFI_DISCONNECT:
                wireless.disconnect(self.wifi_status_callback)

            elif cmd[1] == const.EMAIL_CONFIG:
                print "Email : Start Config"
                arg = ''.join(chr(i) for i in cmd[2:]).split(',')
                param = EmailParam()
                param.username = arg[0]
                param.password = arg[1]
                mail.save_config(self.mail_status_callback, param)

            elif cmd[1] == const.EMAIL_SEND:
                arg = ''.join(chr(i) for i in cmd[2:]).split(',')
                param = EmailParam()
                param.recipient = arg[0]
                param.subject = arg[1]
                param.body = arg[2]
                print "Email : send to %s" % (param.recipient)
                mail.send(self.mail_status_callback, param)

            elif cmd[1] == const.SEND_SMS:
                arg = ''.join(chr(i) for i in cmd[2:]).split(',')
                sms_number = arg[0]
                sms_message = arg[1]
                print "SMS : send to %s" % (sms_number)
                sms.send(self.sms_status_callback, sms_number, sms_message)
                #self.broadcast_to_interface(sms_number, sms_message)

            elif cmd[1] == const.RPI_REBOOT:
                print "Reboot"
                rpi_system.rpi_reboot()

            elif cmd[1] == const.RPI_SHUTDOWN:
                print "Shutdown"
                rpi_system.rpi_shutdown()

            elif cmd[1] == const.RPI_SET_TX_BUFFER:
                print "setting tx buffer[%d] to %d " % (cmd[2], cmd[3])
                self.TX_BUFFER[cmd[2]] = cmd[3]

            elif cmd[1] == const.RPI_NEWRECORDFILE:
                file_name = ''.join(chr(i) for i in cmd[2:])
                print "Logging : creating new log file for %s" % file_name
                self.data_logger.new_log_file(file_name)
                # new
                #loggerdb.truncate(file_name)

            elif cmd[1] == const.RPI_RECORD_TO_RPI:
                # i = 2
                # file_name = ''
                # for c in cmd[2:]:
                #     # loop until we find a comma
                #     if c == ord(','):
                #         break
                #     i += 1
                #     file_name += chr(c)
                #
                # value = (cmd[i+1] << 8) + value[i+2]

                file_name, value = text_cmd[2:].split(',')
                # value = (ord(value[0]) << 8) + (ord(value[1])) # high byte + low byte
                # print "Logging : recording %d as %s" % (value, file_name)

                self.handle_data_logging(file_name, value)


            elif cmd[1] == const.RPI_SHOW_LOG_PLOT:
                file_names, n = text_cmd[2:].split(';')  # n = number of latest points to show
                n = (ord(n[0]) << 8) + (ord(n[1]))  # high byte + low byte

                print "Plotting %d latest points for %s" % (n, file_names)
                self.data_logger.plot(n, file_names)

                self.broadcast_websocket("set_image," + "plot.png")

            elif cmd[1] == const.RPI_USE_RFID:
                print "RFID : Use RFID"
                rfid.useRFID(self.rfid_status_callback, self.rfid_read_tag_callback)

            elif cmd[1] == const.RPI_CLOSE_RFID:
                print "RFID : Use RFID"
                rfid.closeRFID()
            elif cmd[1] == const.RPI_RFID_BEEP:
                rfid.beep()
            elif cmd[1] == const.RPI_WRITE_RFID:
                rfid.write(cmd[2])
            elif cmd[1] == const.RPI_RFID_TAG_FOUND or cmd[1] == const.RPI_RFID_READER_FOUND:
                rfid.updateStatus()
            elif cmd[1] == const.RPI_SAY:
                phrase = ''.join(chr(i) for i in cmd[2:])
                if not self.text2speech.saying_flag:
                    self.broadcast_websocket("say," + phrase)
                    self.text2speech.say(phrase)

            elif cmd[1] == const.RPI_SEND_MESSAGE:
                arg = ''.join(chr(i) for i in cmd[2:]).split(',')
                topic = arg[0]
                message = arg[1]
                print "MESSAGE : %s, %s" % (topic, message)
                self.broadcast_to_interface(topic, message)

        # send the updated TX_BUFFER to the gogo board
        # this transmission needs to be at the end of the loop
        # so that any commands that have modified the buffer
        # value can act on the buffer before it is sent
        self.send_buffer(self.TX_BUFFER)

    def handle_data_logging(self, name=None, value=None):
        value = self.data_logger.validate_number(value)
        if (name is None or value is None):
            return False

        if self.conf.get(self.conf.enable_log_file):
            self.data_logger.log(value, name)

        if self.conf.get(self.conf.enable_log_cloud):
            self.cloud_logger.log(name, value)

        # Broadcast to WS
        packet = {
            "event": "datalog",
            "name": name,
            "datetime": self.data_logger.get_datetime_str(),
            "value": value
        }
        self.broadcast_websocket("%s,%s" % ("datalog", json.dumps(packet)))

        return True
        # log to Database
        # loggerdb.log(value, file_name)

    def handle_rest_api(self, event=None, value1=None, value2=None, arguments={}):
        result_false = {'result': False}
        result = {'result': False}

        try:
            if event == 'keyvalue':
                self.setKeyValueEvent(value1, value2)

            elif event == 'config/email':
                self.conf.save_account(value1, value2)

            elif event == 'config' and value1 == 'pushbullet':
                self.conf.savePushbulletToken(value2)

            elif event == 'config' and (value1 == 'clouddata'):
                self.conf.saveClouddataKey(value2)

            elif event == 'config/wifi':
                self.conf.save_wifi_config(value1, value2)

            elif event == 'wifi/connect':
                wireless.connect(gogod.wifi_status_callback, value1, value2)

            elif event == 'datalog':

                if value1 == 'list':
                    return {'result': True, 'data': self.data_logger.list_all_files()}

                elif value1 == 'get':
                    if (value2.endswith('.json')):
                        result['data'] = self.data_logger.fetch_file(value2,'json')
                    else:
                        result['data'] = self.data_logger.fetch_file(value2)
                    if result['data'] is  not None:
                        result['result'] = True
                        return result
                    return result_false

                elif value1 == 'new' and 'name' in arguments and 'value' in arguments:
                    result['result'] = self.handle_data_logging(arguments['name'], arguments['value'])
                    return result

                elif value1 == 'delete':
                    return {'result': self.data_logger.delete_files(value2)}

                else:
                    return {'result': False}

            elif event == 'addons':

                if value1 == 'list':
                    return {'result': True, 'data': self.addons_mng.list_files()}

                elif value1 == 'get':
                    return self.addons_mng.get_file(value2)

                elif value1 == 'verify':
                    return self.addons_mng.verify(value2)

                elif value1 == 'setting' and arguments == {}:
                    return {'result': True, 'data': self.addons_mng.load_config()}

                elif value1 == 'setting' and arguments != {}:
                    # return {'result':True, 'data': arguments}
                    return self.addons_mng.rest_setting(arguments)

                elif value1 == 'new' and arguments != {}:
                    return self.addons_mng.upload_file(arguments)

            return {'result': True}
        except:
            return result


ws_clients = []  # a dict that tracks the ws connections


class WSHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print 'new image ws connection'
        ws_clients.append(self)

    def on_message(self, message):
        print 'image-ws message received %s' % message

        message = message.split(',')
        if message[0] == "tapped":
            print "Tap event detected"
            gogod.setTapEvent(message[1], message[2])  # send x,y pos as paremeters
        elif message[0] == "keyvalue":
            print "Key Value event detected"
            gogod.setKeyValueEvent(message[1], message[2])  # send key,value as paremeters
            # if "pet_idle.png" in message:
            #     self.write_message("pet_smile.png")
            # else:
            #     self.write_message("pet_idle.png")

    def on_close(self):
        print 'connection closed'
        ws_clients.remove(self)


class ImageHandler(tornado.web.RequestHandler):
    def get(self, story_id):
        self.write(open(os.path.join(MEDIA_PATH, "snapshots", "current.jpg"), "rb").read())


__UPLOADS__ = "uploads/"


class Userform(tornado.web.RequestHandler):
    def get(self):
        self.redirect('/www/index.html')
        return


class Upload(tornado.web.RequestHandler):
    def post(self):
        fileinfo = self.request.files['filearg'][0]
        print "fileinfo is", fileinfo
        fname = fileinfo['filename']
        extn = os.path.splitext(fname)[1]
        cname = str(uuid.uuid4()) + extn
        fh = open(__UPLOADS__ + cname, 'w')
        fh.write(fileinfo['body'])
        self.finish(cname + " is uploaded!! Check %s folder" % __UPLOADS__)


class ScreenHandler(tornado.web.RequestHandler):
    def get(self):
        print "screen handler started"
        ip_list = ip.get_ip_list('eth0')
        if ip_list is None:
            ip_list = ip.get_ip_list('wlan0')
            if ip_list is None:
                self.render("no_ip_error.html")
                return

        # ip_string = "%s.%s.%s.%s" % (str(ip_list[0]), str(ip_list[1]), str(ip_list[2]), str(ip_list[3]))
        ip_string = ".".join(map(str, ip_list))
        print "IP sent to ws client = %s" % ip_string
        self.render("media_template.html", ws_ip=ip_string, current_image=gogod.current_show_image)


class MediaHandler(tornado.web.RequestHandler):
    def get(self, file_name, file_type):
        print "Filename = %s, File Type = %s" % (file_name, file_type)
        if file_type.lower() == 'png':
            self.set_header("Content-type", "image/png")
        elif file_type.lower() == 'jpg':
            self.set_header("Content-type", "image/jpg")
        elif file_type.lower() == 'mp3':
            self.set_header("Content-type", "audio/mpeg")
        elif file_type.lower() == 'ogg':
            self.set_header("Content-type", "audio/ogg")

        else:
            print "Error: unknown media type %s" % file_type
            return

        if os.path.exists(os.path.join(MEDIA_PATH, "%s.%s" % (file_name, file_type))):
            self.write(open(os.path.join(MEDIA_PATH, "%s.%s" % (file_name, file_type)), "rb").read())
        else:
            self.write(open(os.path.join(MEDIA_PATH, "recordings", "%s.%s" % (file_name, file_type)), "rb").read())


class RestAPIHandler(tornado.web.RequestHandler):
    # def set_default_headers(self):
    #    self.set_header("Access-Control-Allow-Origin", "*")

    def post(self):
        return self.handle()

    def get(self):
        return self.handle()

    def handle(self):

        result = {'result': 'error'}
        try:
            event = self.get_argument("event")
            key = self.get_argument("key")
            value = self.get_argument("value")
            if event and key and value:
                result = gogod.handle_rest_api(event, key, value)
            return self.write(result)
        except:
            pass
            #return self.write(result)

        try:
            event = self.get_argument("event")
            value1 = self.get_argument("value1")
            value2 = self.get_argument("value2")
            if event and value1 and value2:
                result = gogod.handle_rest_api(event, value1, value2)
            return self.write(result)
        except:
            self.write(result)


class RestAPI1URLHandler(tornado.web.RequestHandler):
    # def set_default_headers(self):
    #    self.set_header("Access-Control-Allow-Origin", "*")

    def post(self, event=None):
        return self.handle(event)

    def get(self, event=None):
        return self.handle(event)

    def handle(self, event=None):

        result = {'result': 'error'}
        # Check valid API
        if not gogod.conf.is_valid_event(event):
            self.write(result)
        if event == 'config':
            result['result'] = gogod.conf.api_save_config(self.request.arguments)
        else:
            result['data'] = self.request.arguments
        self.write(result)


class RestAPI2URLHandler(tornado.web.RequestHandler):
    # def set_default_headers(self):
    #    self.set_header("Access-Control-Allow-Origin", "*")

    def get(self, event=None, value1=None):
        result = {'result': 'error'}

        if event and value1:
            result = gogod.handle_rest_api(event, value1, None)
        self.write(result)

    def post(self, event=None, value1=None):
        result = {'result': 'error'}
        arguments = {k: self.get_argument(k) for k in self.request.arguments}

        if event and value1:
            if event == 'addons' and value1 == 'new':
                arguments['file'] = self.request.files['file'][0]
            result = gogod.handle_rest_api(event, value1, None, arguments)
        self.write(result)


class RestAPI3URLHandler(tornado.web.RequestHandler):
    # def set_default_headers(self):
    #    self.set_header("Access-Control-Allow-Origin", "*")
    def get(self, event=None, value1=None, value2=None):
        result = {'result': 'error'}

        if event and value1 and value2:
            if value2.endswith(".py"):
                self.set_header("Content-type", "application/x-python")
            result = gogod.handle_rest_api(event, value1, value2)
        self.write(result)


class WWWhtmlHandler(tornado.web.RequestHandler):
    def get(self, uri=None):
        config_data = self.feth_config()
        print "URI GET \t %s" % (uri)

        if uri is None:
            uri = "index"

        elif uri == "webui/index":
            config_data['html_list'] = gogod.webUIfunc.list_html_files()

        elif uri == "addons/index":
            config_data['addons_config'] = gogod.addons_mng.load_config()

        elif uri == "media/html/index":
            config_data['html_list'] = gogod.webUIfunc.list_html_files()
            try:
                pagename = self.get_argument("page")
                if pagename in config_data['html_list']:
                    self.write(gogod.webUIfunc.fetchHTML(pagename))
                    return
            except:
                pass
            # If filename is invalid 
            self.redirect('/www/webui/index.html')

        elif uri == "setting":
            config_data['settings'] = gogod.conf.get_not_credential()

        self.render("%s/%s.html" % (WWW_PATH, uri), config_data=config_data, arguments=self.request.arguments)

    def post(self, uri=None):
        print "URI POST \t %s" % (uri)

        if uri == "rapid_interface_builder/rib_upload":
            result = gogod.webUIfunc.uploadHTML(self.request.arguments)
            self.write(result)
        elif uri == "":
            print "ok"

    def feth_config(self):
        CONFIG_FILE = os.path.join(WWW_PATH, "config.json")
        jsonFile = open(CONFIG_FILE, "r")
        config_data = json.load(jsonFile)
        config_data['hostname_port'] = "%s://%s" % (self.request.protocol, self.request.host)
        config_data['hostname'] = string.replace(config_data['hostname_port'], ':8888', '')
        config_data['header_path'] = os.path.join(WWW_PATH, "include_header.html")
        # config_data['request'] = self.request
        config_data['uri'] = self.request.uri
        config_data['url'] = config_data['hostname_port'] + self.request.uri
        return config_data


class WWWHandler(tornado.web.RequestHandler):
    def get(self, file_name=None):
        print "Filename = %s" % (file_name)
        print file_name.endswith("/")
        # proc = subprocess.Popen("php %s/www/%s" % (APPLICATION_PATH, file_name), shell=True, stdout=subprocess.PIPE)
        # script_response = proc.stdout.read()
        # self.write(script_response)
        if file_name is None:
            self.redirect("/")
            return
        elif file_name.endswith("/"):
            self.redirect('%sindex.html' % (file_name))
            return
        self.write(open("%s/%s.html" % (WWW_PATH, file_name), "rb").read())


class WWWIndexHandler(tornado.web.RequestHandler):
    def get(self, uri=None):
        # self.render("fileuploadform.html")
        self.redirect('/www%s/index.html' % (uri))
        return


ws_addons_clients = []  # a dict that tracks the ws connections

# class WSHandler(tornado.websocket.WebSocketHandler):
#     def check_origin(self, origin):
#         return True

#     def open(self):
#         print 'new image ws connection'
#         ws_clients.append(self)

#     def on_message(self, message):
#         print 'image-ws message received %s' % message

#         message = message.split(',')
#         if message[0] == "tapped":
#             print "Tap event detected"
#             gogod.setTapEvent(message[1], message[2])  # send x,y pos as paremeters
#         elif message[0] == "keyvalue":
#             print "Key Value event detected"
#             gogod.setKeyValueEvent(message[1], message[2])  # send key,value as paremeters

#     def on_close(self):
#         print 'connection closed'
#         ws_clients.remove(self)


class WSAddonsInterfaceHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print 'Addons Interface\tNew Connection'
        ws_addons_clients.append(self)

    def on_message(self, message):
        print 'Addons Interface\treceived %s' % message
        message = message.split(',')
        if len(message) == 1:
            gogod.setKeyValueEvent(message[0], '')
        elif len(message) > 1:
            gogod.setKeyValueEvent(message[0], message[1])

    def on_close(self):
        print 'Addons Interface\tconnection closed'
        ws_addons_clients.remove(self)


application = tornado.web.Application([
    (r"/", Userform),
    (r"/upload", Upload),
    (r"/snapshots/([a-zA-Z]+[0-9]*)", ImageHandler),
    (r'/ws', WSHandler),
    (r'/ws_interface', WSAddonsInterfaceHandler),
    (r'/screen/.+\.html', ScreenHandler),
    (r'/media/(.+)\.(.+)\?*.*', MediaHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': '%s/static' % (APPLICATION_PATH)}),
    (r'/api', RestAPIHandler),
    (r'/api/(.*)/(.*)/(.*)', RestAPI3URLHandler),
    (r'/api/(.*)/(.*)', RestAPI2URLHandler),
    (r'/api/(.*)', RestAPI1URLHandler),
    (r'/www/(.*)\.html', WWWhtmlHandler),
    (r'/www(.*)\/', WWWIndexHandler),
    (r'/www/(.*)', tornado.web.StaticFileHandler, {'path': '%s/www' % (APPLICATION_PATH)}),

])

if __name__ == "__main__":
    gogod = GogoD()
    application.listen(8888, '0.0.0.0')  # '0.0.0.0' prevents error when booted with no available IP assigned
    tornado.ioloop.PeriodicCallback(gogod.update, 500).start()
    tornado.ioloop.IOLoop.instance().start()
