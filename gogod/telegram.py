#!/usr/bin/python

import os, sys
import time
import consolelog
import telepot
import config
import threading
import requests
import re

APPLICATION_PATH        = os.path.abspath(os.path.dirname(sys.argv[0]))
LOG_TITLE               = "Telegram"
_rate_limit_telegram    = 0.25 #seconds
_connected_token        = []
_bot                    = None
_latest_sender_id       = None
_last_worked_token       = None

class TelegramBot():
    def __init__(self, gogod_config=None, sendKeyValue=None):
        global _latest_sender_id
        self.last_handle_time   = 0
        self.conf               = config.Config() if gogod_config is None else gogod_config
        self.sendKeyValue       = sendKeyValue
        self.token              = self.conf.get_telegram_bot_token()
        _latest_sender_id       = self.get_sender()
        consolelog.log(LOG_TITLE, "Created Class")

        self.connect()

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        """ Method that runs forever """
        while True:
            time.sleep(30)
            if _bot is None:
                self.connect()

    def getAPIKey(self):
        self.token = self.conf.get_telegram_bot_token()

    def connect(self):

        self.getAPIKey()
        if not self.token:
            return

        self.bot_thread = TelegramBotThread(self.token, self.conf, self.sendKeyValue)
        self.bot_thread.start()


    def handle_gogo_message(self, message):
        if (time.time() - self.last_handle_time) < _rate_limit_telegram:
            return False
        self.last_handle_time = time.time()

        messages = message.split(',')
        if len(messages) == 1:
            self.send_telegram_message(message)
        elif len(messages) > 1:
            if messages[0] == 'image' or messages[0] == 'picture' or messages[0] == 'photo':
                thread_send_photo = threading.Thread(target=self.send_telegram_photo, args=(messages[1],))
                thread_send_photo.start()
            elif messages[0] == 'message':
                self.send_telegram_message(messages[1])
            else:
                self.send_telegram_message(message)

    def send_telegram_message(self, message):
        global _latest_sender_id, _bot

        if _latest_sender_id is not None and _bot is not None:
            _bot.sendMessage(_latest_sender_id, text=message)

    def send_telegram_photo(self, filename):
        global _latest_sender_id, _bot, _last_worked_token

        if _latest_sender_id is None or _bot is None:
            return

        filepath = self.conf.auto_filepath_image(filename)
        if not os.path.exists(filepath):
            return
        consolelog.log(LOG_TITLE, 'sending image')
        url     = 'https://api.telegram.org/bot%s/sendPhoto' % _last_worked_token
        files   = {'photo': open(filepath, 'rb')}
        data    = {'chat_id': _latest_sender_id,'caption':filename}
        try:
            r       = requests.post(url, data=data, files=files)
            consolelog.log(LOG_TITLE, 'sent result %s' % r.json()['ok'])
        except:
            consolelog.log(LOG_TITLE, 'sent image fail')


    def on_gogo_message(self, title, message):
        if title == "telegram":
            print "%s = %s" %(title, message)
            self.send_telegram_message( "%s" % (message) )

    def save_sender(self, sender_id):
        self.conf.save(self.conf.telegram_bot_sender, sender_id)

    def get_sender(self):
        return self.conf.get(self.conf.telegram_bot_sender)


class TelegramBotThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, token, conf, sendKeyValue):
        super(TelegramBotThread, self).__init__()
        self.count  = 0
        self._stop = threading.Event()

        self.token = token
        self.conf = conf
        self.sendKeyValue = sendKeyValue

        self.latest_sender_id = self.get_sender()
        self.bot = None
        self.is_connected = False

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def save_sender(self, sender_id):
        self.conf.save(self.conf.telegram_bot_sender, sender_id)

    def get_sender(self):
        return self.conf.get(self.conf.telegram_bot_sender)

    def on_telegram_message(self, msg):
        global _latest_sender_id

        content_type, chat_type, chat_id = telepot.glance(msg)
        message = msg['text']

        if self.latest_sender_id != chat_id:
            self.latest_sender_id = chat_id
            _latest_sender_id = chat_id
            self.save_sender(chat_id)

        if self.bot is None:
            return

        for str in ['ping', 'echo']:

            if message.startswith(str):
                message = re.sub(str,'',message,1)
                self.bot.sendMessage(chat_id, message.strip())
                break

        consolelog.log(LOG_TITLE, "message : %s" % message)
        if self.sendKeyValue is not None:
            self.sendKeyValue("telegram", message)

    def send_telegram_message(self, message):
        if self.latest_sender_id is not None and self.bot is not None:
            self.bot.sendMessage(self.latest_sender_id, text=message)

    def run(self):
        global _latest_sender_id, _bot, _last_worked_token

        self.bot = telepot.Bot(self.token)
        if self.token in _connected_token:
            consolelog.log(LOG_TITLE, "already connected")
            return

        try:
            self.bot.getMe()
            self.is_connected = True
            _connected_token.append(self.token)
            _bot = self.bot
            _last_worked_token = self.token
            consolelog.log(LOG_TITLE, "Connected")
        except:
            self.bot = None
            self.is_connected = False
            consolelog.log(LOG_TITLE, "Invalid token")
            return

        self.bot.message_loop({'chat': self.on_telegram_message})

        self.send_telegram_message('Hello, I woke up.')

        while(True):
            if self.stopped():
                return
            time.sleep(1)
