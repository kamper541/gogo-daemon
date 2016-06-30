#!/usr/bin/python
from gogod_interface import GogodInterfacce
import time


def on_message(title, message):
    print "%s = %s" % (title, message)

def main():
    count = 1
    while True:
        time.sleep(5)
        print count
        app.send("count,%s" % count)
        count += 1

app = GogodInterfacce(on_message, main)
