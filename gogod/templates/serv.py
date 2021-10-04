import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web


class WSHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        self.COM_Port = 5
        self.CurrentCommand = 0

        print('new connection')
            # self.write_message("""
            #                    You are connected to the WebSocket Server.
            #                    Type the following commands:
            #                    1 = Set com port
            #                    2 = Beep
            #
            #                    Enter a command number
            #                    """)

    def on_message(self, message):
        print('message received %s' % message)

        if "pet_idle.png" in message:
            #self.write_message("pet_smile.png")

            self.write_message("haha.mp3")
        else:
            self.write_message("pet_idle.png")

        # if self.CurrentCommand == 0:
        #     if message == "1":
        #         self.write_message("Current port is " + str(self.COM_Port+1) + ". Enter a new port number")
        #         self.CurrentCommand = 1
        #     elif message == "2":
        #         self.write_message("Beep")
        #
        # elif self.CurrentCommand == 1:
        #     self.COM_Port = int(message) - 1
        #     self.write_message("Com port set to " + message)
        #     self.CurrentCommand = 0

    def on_close(self):
        print('connection closed')


application = tornado.web.Application([
    (r'/ws', WSHandler),
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()