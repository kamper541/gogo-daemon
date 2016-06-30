#!/usr/bin/env python
# https://python-telegram-bot.org/
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
from gogod_interface import GogodInterfacce
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.CRITICAL)

logger = logging.getLogger(__name__)
logger.propagate = False

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')


def echo(bot, update):
    print "TELEGRAM\t: "+update.message.text
    global _latest_id
    global _bot
    _latest_id = update.message.chat_id
    _bot = bot
    app.send('telegram,%s' % update.message.text)
    bot.sendMessage(update.message.chat_id, text=update.message.text)

def send_to_bot(message=None):
    print _latest_id
    if _latest_id != 0 :
        _bot.sendMessage(_latest_id, text=message)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("<bot's  token>")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.addHandler(CommandHandler("start", start))
    dp.addHandler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.addHandler(MessageHandler([Filters.text], echo))

    # log all errors
    #dp.addErrorHandler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


def on_message(title, message):
    print "%s = %s" %(title, message)
    send_to_bot( "%s, %s" % (title, message) )

_latest_id = 0
_bot = None
print "Telegram bot Starting"
app = GogodInterfacce(on_message, main)

if __name__ == '__main__':
    print "Telegram bot Starting"
    app = GogodInterfacce(on_message, main)
