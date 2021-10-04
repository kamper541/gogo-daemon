#!/usr/bin/python

#-------------------------------------------------------------------------------
# Name          :  Data Logging
# Description   :  Storing sensor's value or data to Database
#                  Self managing queue to insert the data
# Author        :  Marutpong Chailangka
# Created       :  2015-04-24
# Updated       :  2015-08-21
# Updated       :  2015-10-10
# Updated       :  2015-10-12
# Updated       :  2015-11-18
#-------------------------------------------------------------------------------

import pyorient
import datetime
import threading
import Queue
import time
import loggercloud

# Declare the global variables
_queue_records = Queue.Queue()
_db_handle = None
_last_handle = {'field1':0}
_rate_limit = 0.5 #seconds
_clouddata_thread = None

class queueDatabaseThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.keeprunning = True

    def run(self):
        print "Datalog \t: Queue Thread is running"
        global _queue_records
        global _db_handle
        while True:
            if not _queue_records.empty():
                obj = _queue_records.get()
                _db_handle.log_from_queue(obj)
                time.sleep( 0.02 )



class databaseThread(threading.Thread):
    def __init__(self, value, classname):
        threading.Thread.__init__(self)
        self.value = value
        self.classname = classname

    def run(self):
        global _db_handle
        global _clouddata_thread
        if _db_handle==None:
            _db_handle = DatabaseHandle()
            #queue_thread = queueDatabaseThread()
            #_clouddata_thread = loggercloud.CloudDataThread()

            #queue_thread.start()
            #_clouddata_thread.start()

            print("Database \t: new object")
        _db_handle.log(self.value, self.classname)


class DatabaseHandle:
    def __init__(self):
        self.list_exist_class = {}
        # self.init_database()
        self.client = pyorient.OrientDB("localhost", 2424)
        self.dbname = "logger"

    def init_db(self):
        self.client.db_open( self.dbname, "admin", "adminraspberry" )

    def init_class(self ,classname):
        self.init_db()
        if classname in self.list_exist_class:
            pass
        try:
            if not self.exist_class(classname):
                self.client.command( "create class "+classname )
                self.client.command( "CREATE PROPERTY "+classname+".datetime STRING" )
                self.client.command( "CREATE INDEX "+classname+".datetime NOTUNIQUE" )
                self.list_exist_class[classname] = True
                print("Database \t: Created class %s" % (classname))
        except:
            print('Database \t: Unknown Error.')
            pass

    def exist_class(self, classname):
        if classname in self.list_exist_class:
            return True

        exist = False
        try:
            command = "SELECT COUNT(*) FROM ( SELECT expand( classes ) FROM metadata:schema ) WHERE name = '%s'" % (classname)
            result = self.client.query(command)[0]
            if result.COUNT>0:
                self.list_exist_class[classname] = True
                print("Database \t: found class %s" % (classname))
                exist = True
            else:
                # self.client.command( "create class "+classname )
                print("Database \t: Not found class %s" % (classname))
                exist = False

        except:
            print('Database \t: Unknown Error.')
            pass
        return exist

    def sql(self, command):
        self.client.command(command)
        print('Database \t: saved record.')

    def new_name(self, classname):
        self.init_database(classname)

    def log(self, log_value, classname):
        self.init_class(classname)
        command = "insert into %s ( 'datetime', 'value' ) values( '%s', %d )" % (classname, getDatetime(), log_value)
        self.client.command(command)
        self.client.db_close()
        print('Database \t: saved record.')

    def truncate(self, classname):
        self.init_db()
        command = "truncate class %s" % (classname)
        result = self.client.command(command)
        print('Database \t: Clear class %s  success.' % (classname))
        return result

    def drop(self, classnames):
        self.init_db()
        list = classnames.split(",")

        for classname in list:
            command = "drop class " + str(classname)
            print(command)
            result = True
            result = self.client.command(command)
            if result:
                if classname in self.list_exist_class: del self.list_exist_class[classname]
                print('Database \t: Drop class %s  success.' % (classname))
            else:
                print('Database \t: Drop class %s  fail.' % (classname))
                return False
        return True

    def log_from_queue(self, obj):

        if not ( ('name' in obj) and ('value' in obj) and ('datetime' in obj) ):
            print("Database \t: Missing the arguments")
            return False

        log_name = obj['name']
        log_value = obj['value']
        log_datetime = obj['datetime']

        self.init_class(log_name)
        command = "insert into %s ( 'datetime', 'value' ) values( '%s', %s )" % (log_name, log_datetime, log_value)
        self.client.command(command)
        print('Database \t: saved %s => %s' %(log_name,log_value))

    def show(self, classname):
        result = self.client.query( ("SELECT FROM %s") % (classname))

        for doc in result:
            print("---------------------")
            print(doc['value'])
            print(doc['datetime'])

    def fetch_json(self, classname):
        list = []
        result = self.client.query( ("SELECT FROM %s") % (classname))
        for doc in result:
            list.append("[%s:%d]" % (doc['datetime'], doc['value']))
        string = ''.join(list)
        return string

#return a String of Datetime
def getDatetime():
    return time.strftime("%Y-%m-%d %H:%M:%S",time. gmtime())

def initDBThread():
    global _db_handle
    global _clouddata_thread
    if _db_handle==None:
        print("Datalog \t: starting log thread")
        _db_handle = DatabaseHandle()
        queue_thread = queueDatabaseThread()
        _clouddata_thread = loggercloud.CloudDataThread()

        queue_thread.start()
        _clouddata_thread.start()

def truncate(name):
    global _db_handle
    initDBThread()
    _db_handle.truncate(name)

def drop(name):
    global _db_handle
    initDBThread()
    return _db_handle.drop(name)

#handle logging
def log(value, name):
    global _queue_records
    global _db_handle
    global _last_handle
    global _rate_limit
    global _clouddata_thread

    initDBThread()
    #check rate limit
    if name not in _last_handle or (time.time() -_last_handle[name]) >= _rate_limit:

        
        _last_handle[name] = time.time()
        if _clouddata_thread != None:
            _clouddata_thread.prepareData(name,value)

        else :
            _clouddata_thread = loggercloud.CloudDataThread()
            _clouddata_thread.start()

        #print (time.time() -_last_handle[name])
        
        _queue_records.put({'value':value,'name':name, 'datetime':getDatetime()})

        

    #db_thread = databaseThread(value, name)
    #db_thread.start()

# if __name__ == '__main__':
#     _db_handle = DatabaseHandle()
