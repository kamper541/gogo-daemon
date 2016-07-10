# This module uses the 'wifi' package from
#  https://wifi.readthedocs.org
# Updated       :  2015-09-07
# Updated       :  2015-10-10
# Updated       :  2016-07-10
#-------------------------------------------------------------------------------



import wifi
import threading
import os
import ip
import config

_wlan_name = 'wlan0'
_flag_run = False
_flag_disconnected = False
_status_callback = None

class connectWifi(threading.Thread):
    def __init__(self, status_callback, SSID=None, PASSWORD=None):
        threading.Thread.__init__(self)
        self.SSID = SSID
        self.status_callback = status_callback
        self.status = 0  # 0=new, 1=connecting, 2=success, 3=error, 4=ssid not found
        self.status_callback(self.status)

        self.conf = config.Config()

        if PASSWORD is not None:
            self.PASSWORD = PASSWORD.strip()
        else:
            self.PASSWORD = PASSWORD

        if SSID is None and PASSWORD is None:
            self.SSID = self.conf.get(self.conf.wifi_ssid)
            self.PASSWORD = self.conf.get(self.conf.wifi_password)

    def run(self):
        global _flag_run

        if _flag_run or self.SSID is None or self.SSID == "":
            return False

        _flag_run = True
        ssid_found = False
        self.status = 1 # 1=connecting
        self.status_callback(self.status)

        print "Wifi \t\t: connect thread started"
        print "Wifi \t\t: Connecting to SSID %s with password %s" % (self.SSID, self.PASSWORD)

        try:
            os.system("ifup wlan0")
        except:
            self.status = 5  # 5 = Error

        #Checking spacebar
        if ' ' in self.SSID or (self.PASSWORD is not None and ' ' in self.PASSWORD):
            print "Wifi \t\t: invalid config."
            self.status=3 # 3=authentication error
            self.status_callback(self.status)
            _flag_run = False
            return

        # s = wifi.Scheme.find(_wlan_name, self.SSID)
        # if s is not None:
        #     print "found %s in saved configuration" % self.SSID
        #     s.activate()
        #
        # else:
        #     print "No saved config for this network"
        try:
            cells = wifi.Cell.all(_wlan_name)
        except:
            self.status=3 # 3=authentication error
            self.status_callback(self.status)
            _flag_run = False
            return

        for cell in cells:
            if cell.ssid == self.SSID:
                ssid_found = True
                print "Wifi \t\t: SSID %s is found" % self.SSID
                break

        if ssid_found:

            s = wifi.Scheme.find(_wlan_name, self.SSID)
            if s is not None:
                print "Wifi \t\t: Deleting old wifi config"
                s.delete()

            try:
                if self.PASSWORD is not None:
                    scheme = wifi.Scheme.for_cell('wlan0',self.SSID, cell, self.PASSWORD)
                else:
                    scheme = wifi.Scheme.for_cell('wlan0',self.SSID, cell)
            except:
                self.status=3 # 3=authentication error
                self.status_callback(self.status)
                _flag_run = False
                return

            scheme.save()
            self.conf.save_wifi_config(self.SSID, self.PASSWORD)

            print "Wifi \t\t: Now connecting"

            try:
                scheme.activate()
                os.system("ifup wlan0")
                self.status=2 # 2=success
                self.status_callback(self.status)
            except:
                self.status=3 # 3=authentication error
                self.status_callback(self.status)

            print "Wifi \t\t: Done connecting"

            _flag_run = False

        else:
            print "Wifi \t\t: SSID %s not found" % self.SSID
            self.status =4 # 4=ssid not found
            self.status_callback(self.status)

            _flag_run = False


class disconnectWifi(threading.Thread):
    def __init__(self, status_callback):
        threading.Thread.__init__(self)
        self.status_callback = status_callback

    def run(self):
        try:
            os.system("ifdown wlan0")
            self.status = 0 # 0 = idle
        except:
            self.status = 5 # 5 = Error

        self.status_callback(self.status)


def connect(status_callback, SSID, PASSWORD=None):
    global _flag_disconnected
    _flag_disconnected = False
    print "Wifi \t\t: Starting connect thread"
    wifi_thread = connectWifi(status_callback, SSID, PASSWORD)
    wifi_thread.start()

def disconnect(status_callback):
    global _flag_disconnected
    _flag_disconnected = True
    print "Wifi \t\t: Disconnecting to the wireless network"
    disconnect_thread = disconnectWifi(status_callback)
    disconnect_thread.start()

def autoconnect(status_callback=None):
    threading.Timer(30.0, autoconnect).start()
    conf = config.Config()
    if not conf.get_autoconnect_wifi() :
        return

    print "auto wifi"
    global _flag_run
    global _status_callback
    global _flag_disconnected
    
    if status_callback is not None:
        _status_callback = status_callback

    ip_list = ip.get_ip_list('wlan0')
    if ip_list is None and not _flag_run and not _flag_disconnected:
        connect(_status_callback, None, None)




if __name__ == '__main__':

    print "Attempting to Connect to wifi"
    wifi_thread = connectWifi('Annie', 'chiangmai')

    wifi_thread.start()
    print "Exiting main thread"
