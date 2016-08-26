import base64
import os
from os import walk
import sys
import json

APPLICATION_PATH    = os.path.abspath(os.path.dirname(sys.argv[0]))
CONFIG_FILE         = os.path.join(APPLICATION_PATH, "raspberry_setting.json")
HTML_PATH           = os.path.join(APPLICATION_PATH,"www" ,"media", "html")
JSON_PATH           = os.path.join(HTML_PATH, "json")

CONTENT_INCLUDE     = '''<script src="../../bootstrap-material-design/dist/jquery-1.11.min.js"></script>
                    <script src="../../dist/js/reconnecting-websocket.min.js"></script>
                    <script src="../../dist/js/webui_event_handle.js"></script>'''
CONTENT_META        = '<meta  name = "viewport" content = "initial-scale = 1.0, maximum-scale = 1.0, user-scalable = no, minimal-ui"><meta charset="utf-8"/>'


class WebUIFunction():
    def __init__(self):
        print
        print "WebUI\t : init"

    def list_html_files(self):
        exclude_list = ['index.php', 'index.html', '.htaccess']
        file_list = []
        for (dirpath, dirnames, filenames) in walk(HTML_PATH):
            file_list.extend(filenames)
            break
        # filter only html file
        file_list = [e for e in file_list if e not in exclude_list and '.htm' in e]

        return file_list

    def fetchHTML(self, pagename):
        fileContent = self.getFileContent(pagename)

        position = fileContent.find("<head>")
        if position > -1:
            position = position + 6
            fileContent = fileContent[:position] + CONTENT_META + fileContent[position:]

        position_body = fileContent.find("</body>")
        if position_body > - 1:
            fileContent = fileContent[:position_body] + CONTENT_INCLUDE + fileContent[position_body:]

        return fileContent

    def getFileContent(self, pagename):
        full_path = os.path.join(HTML_PATH, pagename)
        if os.path.exists(full_path):
            return open(full_path, "r").read()
        return None

    def checkParametors(self, params):
        return set(['filename', 'html_content', 'confirm', 'json']).issubset(set(params))

    def uploadHTML(self, params):
        result = {'result': False, 'confirm': False, 'result_json': False}
        if not self.checkParametors(params):
            return result
        params['confirm'] = params['confirm'][0] == 'true'
        result['confirm'] = params['confirm']

        filename = params['filename'][0] + '.html'
        json_filename = params['filename'][0] + '.json'

        full_html_path = os.path.join(HTML_PATH, filename)
        full_json_path = os.path.join(JSON_PATH, json_filename)

        # Check file exists?
        result['message'] = (os.path.exists(full_html_path))
        if result['message'] and not params['confirm']:
            result['message'] = 'file_exists'
            return result

        # Write html content to a file.
        htmlFile = open(full_html_path, "w+")
        htmlFile.write(params['html_content'][0])
        htmlFile.close()
        result['result'] = True

        # Write json content to a file.
        jsonFile = open(full_json_path, "w+")
        jsonFile.write(params['json'][0])
        jsonFile.close()
        result['result_json'] = True

        return result
