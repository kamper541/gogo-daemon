#!/usr/bin/python

import logging
import thread
import threading
import time
import websocket

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.CRITICAL)


class GogodInterfacce(threading.Thread):
    def __init__(self, on_inter_message, addons_handler):
        threading.Thread.__init__(self, name="GogodInterfacce")
        super(GogodInterfacce, self).__init__()
        self._stop = threading.Event()
        self.on_inter_message = on_inter_message
        self.addons_handler = addons_handler
        self.start()

    def stop(self):
        self._stop.set()

    def run(self):
        print "Gogod Interfacce \t: starting"
        self.connect()

    def connect(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("ws://localhost:8888/ws_interface",
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open(self.ws)
        # self.addons_handler()
        self.ws.run_forever()

    def send(self, key='', value=''):
        self.ws.send("%s,%s" % (key, value))

    def on_message(self, ws, message):
        print "Gogod Interface \t: msg -> %s" % message
        try:
            message = message.split(',')
            self.on_inter_message(message[0], message[1])
        except:
            print "Gogod Interface \t: msg error"

        '''
        print "PushBullet \t: msg - >" + message
        message = json.loads(message)
        if (message['type'] == "tickle"):
            self.fetch_pushes(self.last_timestamp)
        self.getToken() #For check change token
        '''

    def on_error(self, ws, error):
        print "Gogod Interface \t: Error"
        # print error

    def on_close(self, ws):
        print "Gogod Interface \t: Closed"
        time.sleep(1)
        self.run()

    # def on_open(self, ws):
    #     print "Gogod Interfacce \t: Connected"
    #     #self.addons_handler()

    def on_open(self, ws):
        def run(*args):
            print "Gogod Interface \t: starting..."
            self.addons_handler()
            ws.close()
            print "Gogod Interface \t: terminating..."
        thread.start_new_thread(run, ())


if __name__ == "__main__":
    def on_message(title, message):
        print "%s = %s" % (title, message)


    def main():
        count = 1
        while True:
            time.sleep(5)
            print count
            app.send('count,%s' % count)
            count += 1


    app = GogodInterfacce(on_message, main)
