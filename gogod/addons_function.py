import base64
import os, signal, subprocess
from os import walk
import sys
import json
import config
import time
from easyprocess import EasyProcess

APPLICATION_PATH = os.path.abspath(os.path.dirname(sys.argv[0]))
CONFIG_FILE = os.path.join(APPLICATION_PATH, "raspberry_setting.json")
ADDONS_PATH = os.path.join(APPLICATION_PATH, "addons")
LOG_TITLE = 'Add-ons\t: '


class Timeout(Exception):
    pass


class AddOnsManager():
    def __init__(self, gogod_config=None):
        print LOG_TITLE + "init"
        self.conf = config.Config() if gogod_config is None else gogod_config
        self.running_list = {}
        self.reserved_name = ['__init__.py','checker.py','gogod_interface.py','default.py']

    def list_files(self):

        library_list = []

        for f in os.listdir(os.path.abspath(ADDONS_PATH)):
            module_name, ext = os.path.splitext(f)  # Handles no-extension files, etc.
            if ext == '.py':  # Important, ignore .pyc/other files.
                # print LOG_TITLE+'found %s' % (module_name)
                # module = __import__(module_name)
                library_list.append("%s%s" % (module_name, ext))
        return list(set(library_list) - ( set(self.reserved_name) - set(['default.py']) ) )

    def load_config(self):

        # Load the latest config
        file_list = self.list_files()
        config_list = self.conf.get_addons()

        # Set verification of each file
        for each_file in file_list:
            self.conf.set_addons_verify_status(each_file)

        # Chack the file is exists in config.
        for each_file in config_list:
            if each_file not in file_list:
                self.conf.unset_addons(each_file)

        # get avlid config again
        return self.conf.get_addons()

    def rest_setting(self, arguments):
        result = {'result': False}

        filename = arguments['filename']
        active_cmd = arguments['active']

        if active_cmd == 'true':
            result['start'] = self.start_addons(filename)
            if result['start']['result']:
                self.conf.set_addons_active(filename)
            result['result'] = result['start']['result']
        elif active_cmd == 'false':
            result['start'] = self.stop_addons(filename)
            result['result'] = self.conf.set_addons_deactive(filename)

        return result

    def testrun(self, command, timeout=0.5):

        result = {'result': False}
        pro = EasyProcess(command).call(timeout=timeout)
        if pro.return_code > 0:
            result['error'] = pro.stderr
        else:
            result['result'] = True
        pro.stop()
        return result

    def start_addons(self, filename):

        result = {'result': False, 'error': ''}
        print LOG_TITLE + 'Starting %s' % filename
        # check is already run
        if filename in self.running_list:
            result['error'] = 'Already Run'
            print LOG_TITLE + '%s already run' % filename
            return result

        # Verify the file syntax
        file_verify = self.verify(filename)
        if not file_verify['result']:
            print LOG_TITLE + '%s is verify fail' % filename
            return file_verify

        full_filepath = os.path.join(ADDONS_PATH, filename)
        cmd = "python %s" % full_filepath
        result_testrun = self.testrun(cmd)

        # Verify the file
        if not result_testrun['result']:
            return result_testrun

        pro = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
        # pro = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # out, err = pro.communicate()
        # result['message'] = out
        # result['error'] = err
        # result['result'] = (err == '')
        result['result'] = True

        if result['result']:
            self.running_list[filename] = pro
        # else:
        #     os.killpg(os.getpgid(pro.pid), signal.SIGTERM)  # Send the signal to all the process groups

        print LOG_TITLE + 'Started %s %s' % (filename, result['result'])
        return result

    def stop_addons(self, filename):

        result = {'result': True}

        if filename in self.running_list:
            print LOG_TITLE + 'Terminating %s' % filename
            pro = self.running_list[filename]
            os.killpg(os.getpgid(pro.pid), signal.SIGTERM)  # Send the signal to all the process groups
            del self.running_list[filename]
            result['result'] = True
            print LOG_TITLE + 'Terminated %s' % filename
        else:
            print LOG_TITLE + ' %s not run' % filename

        return result

    def verify(self, filename):
        filename = os.path.join(ADDONS_PATH, filename)
        print filename
        if not os.path.exists(filename):
            return {'result': False, 'error': 'No file exist.'}

        cmd = "python -m py_compile %s" % filename

        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        # print err
        return {'result': err == "", 'error': err}

    def upload_file(self, params):

        result = {'result': False}
        confirm = params['confirm'] == 'true'
        filename = params['file']['filename']
        full_file_path = os.path.join(ADDONS_PATH, filename)
        print LOG_TITLE + 'file named %s' % filename

        #Check is a reserved name
        if filename in self.reserved_name:
            result['message'] = 'file_reserved'
            print LOG_TITLE + 'file reserved'
            return result

        # Check file exists?
        result['message'] = (os.path.exists(full_file_path))
        if result['message'] and not confirm:
            result['message'] = 'file_exists'
            print LOG_TITLE + 'file exists'
            return result

        # Write html content to a file.
        htmlFile = open(full_file_path, "w+")
        htmlFile.write(params['file']['body'])
        htmlFile.close()
        result['result'] = True

        return result

    def get_file(self, filename):
        full_file_path = os.path.join(ADDONS_PATH, filename)
        print LOG_TITLE + 'getting file %s' % filename
        if (os.path.exists(full_file_path)):
            return open(full_file_path, "rb").read()
        return ""


if __name__ == '__main__':
    addons = AddOnsManager()
    print addons.list_files()
