import subprocess
import threading
import gammu
import os
import consolelog

GAMMU_CONFIG_FILE   = "/root/.gammurc"
USB_CONFIG_FILE     = "/etc/usb_modeswitch.conf"
LOG_TITLE           = "SMS"

class SmsStatus(object):
    NEW                 = 0
    SENDING             = 1
    SUCCESS             = 2
    ERROR               = 3
    ERR_DEVICENOTEXIST  = 4
    ERR_NOSIM           = 5


class SmsHandle(threading.Thread):
    def __init__(self, status_callback, sms_number, sms_message):
        threading.Thread.__init__(self)
        self.status_callback = status_callback
        self.status = SmsStatus.NEW
        self.status_callback(self.status)
        self.sms_number = sms_number
        self.sms_message = sms_message


    def config(self):
        if not os.path.exists(GAMMU_CONFIG_FILE):
            consolelog.log(LOG_TITLE, "No gammu config File")
            gammu_config_content = '''[gammu]

port = /dev/ttyUSB0
model =
connection = at19200
synchronizetime = yes
logfile =
logformat = nothing
use_locking =
gammuloc =
            '''

            file = open(GAMMU_CONFIG_FILE, "w+")
            file.write(gammu_config_content)
            file.close()
            consolelog.log(LOG_TITLE, "Written config to file")


        if 'DefaultVendor' not in open(USB_CONFIG_FILE).read():
            consolelog.log(LOG_TITLE, "No Device config")
            modeswitch_content = '''DefaultVendor= 0x12d1
DefaultProduct = 0x1446
TargetVendor = 0x12d1
TargetProductList ="1001,1406,140b,140c,141b,14ac"
CheckSuccess = 20
MessageContent ="55534243123456780000000000000011060000000000000000000000000000"'''

            file = open(USB_CONFIG_FILE, 'a')
            file.write(modeswitch_content)
            file.close()
            consolelog.log(LOG_TITLE, "Written device config")

        os.system("sudo usb_modeswitch -c /etc/usb_modeswitch.conf")

    def run(self):
        self.status = SmsStatus.SENDING
        self.status_callback(self.status)
        consolelog.log(LOG_TITLE, "thread started")
        self.config()
        try:
            #command_string = 'sudo gammu sendsms TEXT ' + self.sms_number + ' -textutf8 "' + self.sms_message + '" '
            #print commands.getoutput(command_string)
            self.status = SmsStatus.ERROR
            sm = gammu.StateMachine()
            sm.ReadConfig()
            sm.Init()
            message = {
                'Text': self.sms_message,
                'SMSC': {'Location': 1},
                'Number': self.sms_number,
            }
            # Actually send the message
            result = sm.SendSMS(message)
            consolelog.log(LOG_TITLE, "Send sms Success")
            self.status = SmsStatus.SUCCESS
        except gammu.ERR_DEVICENOTEXIST:
            consolelog.log(LOG_TITLE, "Error device doesn't exist")
            self.status = SmsStatus.ERR_DEVICENOTEXIST
        except gammu.ERR_NOSIM:
            consolelog.log(LOG_TITLE, "Error can not access SIM card")
            self.status = SmsStatus.ERR_NOSIM
        except ValueError:
            consolelog.log(LOG_TITLE, "Error")
            self.status = SmsStatus.ERROR
        self.status_callback(self.status)


def read_all_sms():
    sm = gammu.StateMachine()
    sm.ReadConfig()
    sm.Init()

    status = sm.GetSMSStatus()

    smsCount = status['SIMUsed']

    print("SMS count = " + str(smsCount))

    for i in range(0,smsCount):
         if i==0:
            sms = sm.GetNextSMS(Folder=0, Start=True)
         else:
            sms = sm.GetNextSMS(Folder=0, Location=i-1)
         print(sms[0]['Number'])     # Sender's phone number
         print (sms[0]['DateTime'])   # Receive date and time
         print (sms[0]['State'])      # message state (unread/read)
         print (sms[0]['Text'])       # SMS content
         print ("==================================")

    print("Done")


def send(status_callback, sms_number, sms_message):
    consolelog.log(LOG_TITLE, "starting sms thread")
    sms_thread = SmsHandle(status_callback, sms_number, sms_message)
    sms_thread.start()

#command response
#Sending SMS 1/1....waiting for network answer..OK, message reference=1
#Sending SMS 1/1....waiting for network answer..OK, message reference=2
#Can not access SIM card.
