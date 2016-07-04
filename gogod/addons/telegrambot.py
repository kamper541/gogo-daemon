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

_bot    = None
_token  = None

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

def send_to_bot(message=None):
    print _latest_sender_id
    if _latest_sender_id is not None :
        _bot.sendMessage(_latest_sender_id, text=message)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def echo(bot, update):
    print "TELEGRAM\t: "+update.message.text
    global _latest_sender_id
    global _bot
    _bot = bot

    if _latest_sender_id != update.message.chat_id:
        _latest_sender_id = update.message.chat_id
        app.save_variable('telegram_sender', _latest_sender_id)

    on_telegram_message(bot, update)
    bot.sendMessage(update.message.chat_id, text=update.message.text)

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(_token)

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

def on_telegram_message(bot, update):
    message = update.message.text
    app.send("telegram", "%s" % message)

def on_message(title, message):
    if title == "telegram":
        print "%s = %s" %(title, message)
        send_to_bot( "%s" % (message) )

if __name__ == '__main__':
    print "Telegram bot Starting"

    _token = "< API Token >"

    app = GogodInterfacce(on_message, main)

    _latest_sender_id = app.get_variable('telegram_sender')
