#!/usr/bin/python
from gogod_interface import GogodInterfacce
import time


def on_message(title, message):
    print("\t %s = %s" % (title, message))
    # Do something when received the message.

def main():

    # An example to getting a variable from storage
    count = 1

    while True:
        time.sleep(5)
        print("sending topic=count  message=%s" % count)

        # An example to sending a topic/message to GoGo Board
        app.send("count", count)
        count += 1


app = GogodInterfacce(on_message, main)
