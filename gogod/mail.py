#!/usr/bin/python

#-------------------------------------------------------------------------------
# Name          :  Gmail Sender
# Description   :  Gmail SMTP email sender with encryption configuration file.
# Author        :  Marutpong Chailangka
# Created       :  2014-11-30
# Updated       :  2015-07-21
#-------------------------------------------------------------------------------

import smtplib
import threading
from Crypto.Cipher import AES
import base64
import os
import sys
import json
import config

APPLICATION_PATH = os.path.abspath(os.path.dirname(sys.argv[0]))
isSending = False


class EmailStatus(object):
    NEW                 = 0
    CONNECTING          = 1
    SUCCESS             = 2
    ERROR_CONNECTION    = 3
    ERROR_AUTHEN        = 4
    ERROR_CONFLICT      = 5
    ERROR               = 6


class EmailParam:
    def __init__(self):
        self.username = None
        self.username = None
        self.password = None
        self.recipient = None
        self.subject = None
        self.body = None


class EmailHandle(threading.Thread):
    def __init__(self, status_callback, param):
        threading.Thread.__init__(self)
        self.status_callback = status_callback
        self.status = EmailStatus.NEW
        self.status_callback(self.status)
        self.param = param

        self.conf = config.Config(status_callback)
        self.conf.EmailStatus = EmailStatus

    def run(self):
        global isSending
        isSending = True
        self.status = EmailStatus.CONNECTING
        self.status_callback(self.status)
        print "Email : thread started"

        #Get decrypted account infomation form text file
        self.get_account()
        GMAIL_USERNAME = self.param.username
        GMAIL_PASSWORD = self.param.password
        recipient = self.param.recipient
        email_subject = self.param.subject
        body_of_email = self.param.body
        # The below code never changes, though obviously those variables need values.
        try:
            print "Email : Connecting to Gmail"
            self.status = EmailStatus.ERROR_CONNECTION
            session = smtplib.SMTP('smtp.gmail.com', 587)
            session.ehlo()
            session.starttls()

            self.status = EmailStatus.ERROR_AUTHEN
            session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

            self.status = EmailStatus.ERROR
            headers = "\r\n".join(["from: " + GMAIL_USERNAME,
                        "subject: " + email_subject,
                        "to: " + recipient,
                        "mime-version: 1.0",
                        "content-type: text/plain"])
            # body_of_email can be plaintext or html!
            content = headers + "\r\n\r\n" + body_of_email
            session.sendmail(GMAIL_USERNAME, recipient, content)
            print "Email : email has sent"
            self.status = EmailStatus.SUCCESS
            self.status_callback(self.status)
        except:
            print "Email : error"
            self.status_callback(self.status)
        isSending = False

    def get_account(self):
        self.param = self.conf.get_account(self.param)


def save_config(status_callback, param):
    print "Email : Saving email config"
    conf = config.Config(status_callback)
    conf.EmailStatus = EmailStatus
    conf.save_account(param.username,param.password)


def send(status_callback, param):

    if isSending:
        print "Email : conflict sending "
        status_callback(EmailStatus.ERROR_CONFLICT)
    else:
        print "Email : starting connect thread"
        email_thread = EmailHandle(status_callback, param)
        email_thread.start()

if __name__ == '__main__':
    if len(sys.argv)==3:
        enc = Encryption()
        arguments = sys.argv
        encrypted = enc.save_config(arguments[1], arguments[2])
    else:
        print 'false'