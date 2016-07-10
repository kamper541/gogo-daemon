import os, signal, subprocess
import sys
import config
import re
from easyprocess import EasyProcess
import consolelog

APPLICATION_PATH    = os.path.abspath(os.path.dirname(sys.argv[0]))
CONFIG_FILE         = os.path.join(APPLICATION_PATH, "raspberry_setting.json")
ADDONS_PATH         = os.path.join(APPLICATION_PATH, "addons")
LOG_TITLE           = "Add-ons"


class Timeout(Exception):
    pass


class AddOnsManager():
    def __init__(self, gogod_config=None):
        consolelog.log(LOG_TITLE, "init")
        self.conf = config.Config() if gogod_config is None else gogod_config
        self.running_list = {}
        self.reserved_name = ['__init__.py','checker.py','gogod_interface.py','example.py']
        self.autorun()

    def list_files(self):

        library_list = []

        for f in os.listdir(os.path.abspath(ADDONS_PATH)):
            module_name, ext = os.path.splitext(f)  # Handles no-extension files, etc.
            if ext == '.py':  # Important, ignore .pyc/other files.
                consolelog.log(LOG_TITLE, 'found %s' % (module_name))
                # module = __import__(module_name)
                library_list.append("%s%s" % (module_name, ext))
        return list(set(library_list) - ( set(self.reserved_name) - set(['example.py']) ) )

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

    def autorun(self):
        config_list = self.load_config()

        for filename in config_list:
            if config_list[filename]['verify'] and config_list[filename]['active']:
                self.start_addons(filename)


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
        pro = EasyProcess(command.split()).call(timeout=timeout)
        if pro.return_code > 0:
            result['error'] = pro.stderr
        else:
            result['result'] = True
        pro.stop()
        return result

    def start_addons(self, filename):

        result = {'result': False, 'error': ''}
        consolelog.log(LOG_TITLE, 'Starting %s' % filename)
        # check is already run
        if filename in self.running_list:
            result['error'] = 'Already Run'
            consolelog.log(LOG_TITLE, '%s already run' % filename)
            return result

        # Verify the file syntax
        file_verify = self.verify(filename)
        if not file_verify['result']:
            consolelog.log(LOG_TITLE, 'verify %s fail' % filename)
            return file_verify

        full_filepath = os.path.join(ADDONS_PATH, filename)
        cmd = 'python %s' % full_filepath
        result_testrun = self.testrun(cmd)

        # Verify the file
        if not result_testrun['result']:
            return result_testrun

        pro = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
        # out, err = pro.communicate()
        # result['message'] = out
        # result['error'] = err
        # result['result'] = (err == '')
        result['result'] = True

        if result['result']:
            self.running_list[filename] = pro
        # else:
        #     os.killpg(os.getpgid(pro.pid), signal.SIGTERM)  # Send the signal to all the process groups

        consolelog.log(LOG_TITLE, 'Started %s %s' % (filename, result['result']))
        return result

    def stop_addons(self, filename):

        result = {'result': True}

        if filename in self.running_list:
            consolelog.log(LOG_TITLE, 'Terminating %s' % filename)
            pro = self.running_list[filename]
            os.killpg(os.getpgid(pro.pid), signal.SIGTERM)  # Send the signal to all the process groups
            del self.running_list[filename]
            result['result'] = True
            consolelog.log(LOG_TITLE, 'Terminated %s' % filename)
        else:
            consolelog.log(LOG_TITLE, ' %s is not run' % filename)

        return result

    def verify(self, filename):
        filename = os.path.join(ADDONS_PATH, filename)
        if not os.path.exists(filename):
            return {'result': False, 'error': 'No file exist.'}

        cmd = r'python -m py_compile %s' % filename
        # p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        # print err
        return {'result': err == "", 'error': err}

    def corect_filename(self, name):
        name = re.sub('[^a-zA-Z0-9 \n\.]', '', name)
        return name.replace(" ", "_")

    def upload_file(self, params):

        result = {'result': False}
        confirm = params['confirm'] == 'true'
        filename = self.corect_filename(params['file']['filename'])

        full_file_path = os.path.join(ADDONS_PATH, filename)
        consolelog.log(LOG_TITLE, 'file named %s' % filename)

        #Check is a reserved name
        if filename in self.reserved_name:
            result['message'] = 'file_reserved'
            consolelog.log(LOG_TITLE, 'file reserved')
            return result

        # Check file exists?
        result['message'] = (os.path.exists(full_file_path))
        if result['message'] and not confirm:
            result['message'] = 'file_exists'
            consolelog.log(LOG_TITLE, 'file exists')
            return result

        # Write html content to a file.
        htmlFile = open(full_file_path, "w+")
        htmlFile.write(params['file']['body'])
        htmlFile.close()
        result['result'] = True

        return result

    def get_file(self, filename):
        full_file_path = os.path.join(ADDONS_PATH, filename)
        consolelog.log(LOG_TITLE, 'getting file %s' % filename)
        if (os.path.exists(full_file_path)):
            return open(full_file_path, "rb").read()
        return ""


if __name__ == '__main__':
    addons = AddOnsManager()
    print addons.list_files()
