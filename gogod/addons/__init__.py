#!/usr/bin/python
from . import *
import os, sys, threading, time
#import default

class Addons (threading.Thread):
    def __init__(self,APPLICATION_PATH, sendKeyValue):
        threading.Thread.__init__(self)
        self.APPLICATION_PATH = APPLICATION_PATH
        self.sendKeyValue = sendKeyValue
        
    def run(self):
        
        time.sleep(2)
        self.main(os.path.join(self.APPLICATION_PATH, "addons"))
                    
    def import_libs(self, dir):
        
        library_list = [] 
        
        for f in os.listdir(os.path.abspath(dir)):       
            module_name, ext = os.path.splitext(f) # Handles no-extension files, etc.
            #if module_name != '__init__' and ext == '.py': # Important, ignore .pyc/other files.
                ##print 'Addons \t: imported %s' % (module_name)
                #module = __import__(module_name)
                #library_list.append(module)
                #module.sendKeyValue = self.sendKeyValue
        
        return library_list
        
    def main(self, dir):

        if os.path.isdir(dir):
            sys.path.append(dir)
        else:
            print '%s is not a directory!' % (dir)
        lib_list = self.import_libs(dir)
        
        for l in lib_list:
            self.filter_builtins(l)
            

    def filter_builtins(self, module):
        """ Filter out the builtin functions, methods from module """

        # Default builtin list    
        built_in_list = ['__builtins__', '__doc__', '__file__', '__name__']
        
        # Append anything we "know" is "special"
        # Allows your libraries to have methods you will not try to exec.
        built_in_list.append('special_remove')

        # get the list of methods/functions from the module
        module_methods = dir(module) # Dir allows us to get back ALL methods on the module.

        for b in built_in_list:
            if b in module_methods:
                module_methods.remove(b)

        # print module_methods
        return module_methods
