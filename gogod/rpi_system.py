import os

def rpi_reboot():
    os.system("reboot")

def rpi_shutdown():
    os.system("halt")