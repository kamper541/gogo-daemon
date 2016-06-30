import urllib, pycurl, os
import threading
import time


class Google(threading.Thread):
    def __init__(self, phrase):
        threading.Thread.__init__(self)
        self.phrase = phrase

    @staticmethod
    def downloadFile(url, fileName):
        fp = open(fileName, "wb")
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, fp)
        curl.perform()
        curl.close()
        fp.close()

    @staticmethod
    def getGoogleSpeechURL(phrase):
        googleTranslateURL = "http://translate.google.com/translate_tts?tl=en&"
        parameters = {'q': phrase}
        data = urllib.urlencode(parameters)
        googleTranslateURL = "%s%s" % (googleTranslateURL, data)
        return googleTranslateURL

    def say(self, phrase):
        googleSpeechURL = self.getGoogleSpeechURL(phrase)
        self.downloadFile(googleSpeechURL, "tts.mp3")
        os.system("mplayer tts.mp3 -af extrastereo=0 &")

    def run(self):
        self.say(self.phrase)


class Festival(threading.Thread):
    def __init__(self, set_flag, phrase):
        threading.Thread.__init__(self)
        self.phrase = phrase
        self.set_flag = set_flag

    def run(self):
        self.set_flag(True)
        start = time.time()
        print "Text2Speech : Saying " + self.phrase
        os.system("echo \"" + self.phrase + "\" | festival --tts")
        end = time.time() - start
        print "Text2Speech : End, time used %f s" % end
        self.set_flag(False)


class Espeak(threading.Thread):
    def __init__(self, phrase):
        threading.Thread.__init__(self)
        self.phrase = phrase

    def run(self):
        print "Text2Speech : Saying " + self.phrase
        os.system("espeak -ven+f3 -k5 -s150 \"" + self.phrase + "\"")
        print "Text2Speech : End"


class TextToSpeech:

    def __init__(self):
        self.saying_flag = False
        self.dubuging = False

    def set_flag(self, state):
        if self.dubuging:
            print "Text2Speech : state cahnge to "+str(self.saying_flag)
        self.saying_flag = state

    def say(self, phrase):
        if self.dubuging:
            print "Text2Speech : "+str(self.saying_flag)
        if not self.saying_flag:
            speech2 = Festival(self.set_flag, phrase)
            speech2.start()


def say(phrase):
    # speech = Google(phrase)
    # speech.run()
#    speech2 = Festival(phrase)
#    speech2.run()
        # speech3 = Espeak(phrase)
        # speech3.run()
    text2speech = TextToSpeech()
    text2speech.say(phrase)