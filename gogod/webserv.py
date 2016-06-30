import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("You requested the main page")

class ImageHandler(tornado.web.RequestHandler):
    def get(self, story_id):

        self.write(open("./snapshots/current.jpg", "rb").read())


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/snapshots/([a-zA-Z]+[0-9]*)", ImageHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()