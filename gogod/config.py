#!/usr/bin/python

# -------------------------------------------------------------------------------
# Name          :  Configuration Reader and Writer and Encryption
# Description   :
# Author        :  Marutpong Chailangka
# Created       :  2015-08-21
# Updated       :  2015-08-21
# Updated       :  2015-11-18
# Updated       :  2015-12-12
# Updated       :  2016-03-16
# Updated       :  2016-05-05
# -------------------------------------------------------------------------------

from Crypto.Cipher import AES
import base64
import os
from os import walk
import sys
import json
import subprocess

APPLICATION_PATH    = os.path.abspath(os.path.dirname(sys.argv[0]))
CONFIG_FILE         = os.path.join(APPLICATION_PATH, "raspberry_setting.json")
HTML_PATH           = os.path.join(APPLICATION_PATH, "www", "media", "html")
ADDONS_PATH         = os.path.join(APPLICATION_PATH, "addons")


class Config():
    def __init__(self, status_callback=None):

        self.status_callback = status_callback
        self.enc = Encryption()
        self.wifi_ssid          = "wifi_ssid"
        self.wifi_password      = "wifi_password"
        self.gmail_username     = "gmail_username"
        self.gmail_password     = "gmail_password"
        self.pushbullet_token   = "pushbullet_token"
        self.clouddata_key      = "clouddata_key"
        self.autoconnect_wifi   = "autoconnect_wifi"
        self.enable_log_file    = "enable_log_file"
        self.enable_log_cloud   = "enable_log_cloud"
        self.addons             = "addons"
        self.current            = self.get_all()

        self.api_events = ['keyvalue', 'datalog', 'wifi', 'config']
        self.valid_configs = [self.wifi_ssid, self.wifi_password, self.gmail_username, self.gmail_password,
                              self.pushbullet_token, self.clouddata_key, self.autoconnect_wifi, self.enable_log_file,
                              self.enable_log_cloud, self.addons]

    def get_not_credential(self):
        data = self.get_all()
        return {self.autoconnect_wifi: data[self.autoconnect_wifi]
                , self.enable_log_file:data[self.enable_log_file]
                , self.enable_log_cloud: data[self.enable_log_cloud]

                }

    def get_all(self):
        if os.path.exists(CONFIG_FILE):
            jsonFile = open(CONFIG_FILE, "r")
            data = json.load(jsonFile)
            data[self.autoconnect_wifi] = self.is_true(data[self.autoconnect_wifi])
            data[self.enable_log_file] = self.is_true(data[self.enable_log_file])
            data[self.enable_log_cloud] = self.is_true(data[self.enable_log_cloud])
            return data
        return {}

    def is_true(self, value):
        return value in (True, "yes", "True", "true", "t", "1")

    def get(self, name):
        data = self.get_all()
        if name in data:
            if name == self.gmail_password:
                return self.enc.DecodeAES(data[name])
            return data[name]
        if name == self.addons:
            return {}
        return None

    def save_to_file(self, params):

        if self.status_callback is not None and (self.gmail_username in params or self.gmail_password in params):
            self.status_callback(10 + self.EmailStatus.CONNECTING)

        data = {}
        if os.path.exists(CONFIG_FILE):
            jsonFile = open(CONFIG_FILE, "r")
            data = json.load(jsonFile)
            jsonFile.close()

            for key, value in params.iteritems():

                if not self.is_valid_config_name(key):
                    continue

                if key == self.gmail_password:
                    value = None if value == "None" else value
                    data[key] = self.enc.EncodeAES(value)
                else:
                    data[key] = value

                self.current[key] = value


            jsonFile = open(CONFIG_FILE, "w+")
            jsonFile.write(json.dumps(data))
            jsonFile.close()

        # Backup old account
        # if (os.path.exists(self.ENCRYPT_FILE)):
        #     os.rename(self.ENCRYPT_FILE, self.ENCRYPT_FILE+".bak")
        # file = open(self.ENCRYPT_FILE, "w")
        # file.write(param.username + "\n")
        # file.write(self.encrypt(self.ENCRYPT_PASSWORD, param.password) + "\n")
        # file.close()

        print("Config : Save configuration Success")

        if self.status_callback is not None:
            self.status_callback(10 + self.EmailStatus.SUCCESS)

    def save(self, name=None, value=None):
        result = False

        if name == self.pushbullet_token:
            result = self.savePushbulletToken(value)

        elif name == self.clouddata_key:
            result = self.saveClouddataKey(value)

        elif self.is_valid_config_name(name):
            result = self.save_to_file({name: value})

        return result

    def get_addons(self, name=None):
        if name is None:
            return self.get(self.addons)
        return self.get(self.addons)[name]

    def set_addons_active(self, name=None):

        if not self.verify_python(os.path.join(ADDONS_PATH, name))['result']:
            return False

        current_config = self.get_addons(None)

        if name not in current_config:
            current_config[name] = {'active': True}
        current_config[name]['active'] = True

        self.save(self.addons, current_config)
        return True

    def set_addons_deactive(self, name=None):

        if not self.verify_python(os.path.join(ADDONS_PATH, name))['result']:
            return False

        current_config = self.get_addons(None)

        if name not in current_config:
            current_config[name] = {'active': False}
        current_config[name]['active'] = False

        self.save(self.addons, current_config)
        return True

    def set_addons_verify_status(self, name=None):

        verify_status = self.verify_python(os.path.join(ADDONS_PATH, name))['result']
        current_config = self.get_addons(None)

        if name not in current_config:
            current_config[name] = {'verify': verify_status,'active': False}
        current_config[name]['verify'] = verify_status
        #current_config[name]['active'] = False if not verify_status else current_config[name]['active']

        self.save(self.addons, current_config)
        return True

    def unset_addons(self, name=None):

        current_config = self.get_addons(None)

        if name in current_config:
            del current_config[name]
            self.save(self.addons, current_config)

        return True

    def verify_python(self, filename):
        cmd = "python -m py_compile %s" % filename
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        #print err
        return {'result': err == "", 'error': err}

    def get_account(self, param):
        print "Config : Getting email account"
        param.username = self.get(self.gmail_username)
        param.password = self.get(self.gmail_password)
        return param

    def save_account(self, username, password):
        print "Config : Saving email account"
        self.save_to_file({self.gmail_username: username, self.gmail_password: password})
        return True

    def get_autoconnect_wifi(self):
        # print "Config : Getting autoconnect_wifi"
        return self.get(self.autoconnect_wifi)

    def save_autoconnect_wifi(self, value):
        print "Config : Saving autoconnect_wifi"
        self.save_to_file({self.autoconnect_wifi: value})
        return True

    def save_wifi_config(self, ssid, password):
        print "Config : Saving wifi config"
        self.save_to_file({self.wifi_ssid: ssid, self.wifi_password: password})
        return True

    def getPushbulletToken(self):
        # print "Config : Getting Pushbullet Token"
        return self.get(self.pushbullet_token)

    def savePushbulletToken(self, token):
        self.save_to_file({self.pushbullet_token: token})

    def getClouddataKey(self):
        if self.get(self.clouddata_key):
            return self.get(self.clouddata_key).strip()
        return None

    def saveClouddataKey(self, key):
        self.save_to_file({self.clouddata_key: key})

    def list_html_files(self):
        exclude_list = ['index.php', 'index.html', '.htaccess']
        file_list = []
        for (dirpath, dirnames, filenames) in walk(HTML_PATH):
            file_list.extend(filenames)
            break

        # filter only html file
        file_list = [e for e in file_list if e not in exclude_list and '.htm' in e]
        return file_list

    def api_save_config(self, params):

        if 'raspberry-pi' not in params:
            return False
        del params['raspberry-pi']

        for param in params:
            param_stripped = self.trim_left(param, "input_")
            if self.is_valid_config_name(param_stripped) and params[param] != [''] and len(params[param]) == 1:
                value = params[param][0]
                self.save(param_stripped, value)

        return True;

    def is_valid_event(self, event):
        return event in self.api_events

    def is_valid_config_name(self, name):
        return name in self.valid_configs

    def trim_left(self, word, trim):
        if word.startswith(trim):
            return word[len(trim):]
        return word


# Encryption
class Encryption:
    def __init__(self):
        self.config_file = os.path.join(APPLICATION_PATH, "raspberry_setting.json")
        self.key = "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x11\x12\x13\x14\x15\x16"
        self.iv = "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x11\x12\x13\x14\x15\x16"
        self.replace_plus = "BIN00101011BIN"

        # the block size for the cipher object; must be 16, 24, or 32 for AES
        self.BLOCK_SIZE = 16
        self.pad = lambda s: s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) \
                                 * chr(self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE)
        self.unpad = lambda s: s[0:-ord(s[-1])]

    def repeat_to_length(self, string_to_expand, length):
        return (string_to_expand * ((length / len(string_to_expand)) + 1))[:length]

    def EncodeAES(self, s):
        c = AES.new(self.key, AES.MODE_CBC, self.iv)
        s = self.pad(s)
        s = c.encrypt(s)
        s = base64.b64encode(s)
        return s.replace("+", self.replace_plus)

    def DecodeAES(self, enc):
        c = AES.new(self.key, AES.MODE_CBC, self.iv)
        enc = enc.replace(self.replace_plus, "+")
        enc = base64.b64decode(enc)
        enc = c.decrypt(enc)
        return self.unpad(enc)

    def encrypt_interface(self, input_password):
        return self.encrypt(self.ENCRYPT_PASSWORD, input_password)


if __name__ == "__main__":
    con = Config()
    #print con.set_addons_enable_active('telegrambot.py')
    print con.get_addons()
