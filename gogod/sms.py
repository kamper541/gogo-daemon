import commands
import threading
import gammu


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

    def run(self):
        self.status = SmsStatus.SENDING
        self.status_callback(self.status)
        print "SMS : thread started"
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
            print("SMS : Send sms Success")
            self.status = SmsStatus.SUCCESS
        except gammu.ERR_DEVICENOTEXIST:
            print "SMS : Error device doesn't exist"
            self.status = SmsStatus.ERR_DEVICENOTEXIST
        except gammu.ERR_NOSIM:
            print "SMS : Error can not access SIM card"
            self.status = SmsStatus.ERR_NOSIM
        except ValueError:
            print "SMS : error"
            self.status = SmsStatus.ERROR
        self.status_callback(self.status)


def read_all_sms():
    sm = gammu.StateMachine()
    sm.ReadConfig()
    sm.Init()

    status = sm.GetSMSStatus()

    smsCount = status['SIMUsed']

    print "SMS count = " + str(smsCount)

    for i in range(0,smsCount):
         if i==0:
            sms = sm.GetNextSMS(Folder=0, Start=True)
         else:
            sms = sm.GetNextSMS(Folder=0, Location=i-1)
         print sms[0]['Number']     # Sender's phone number
         print sms[0]['DateTime']   # Receive date and time
         print sms[0]['State']      # message state (unread/read)
         print sms[0]['Text']       # SMS content
         print "=================================="

    print "Done"


def send(status_callback, sms_number, sms_message):
    print "SMS : starting sms thread"
    sms_thread = SmsHandle(status_callback, sms_number, sms_message)
    sms_thread.start()

#command response
#Sending SMS 1/1....waiting for network answer..OK, message reference=1
#Sending SMS 1/1....waiting for network answer..OK, message reference=2
#Can not access SIM card.
