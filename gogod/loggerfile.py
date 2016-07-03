import os
import os.path
import datetime
#import matplotlib
#matplotlib.use('Agg')  # this tells matplotlib that we are not plotting to the screen. It must be here.
#import matplotlib.pyplot as plt
import subprocess
from os import walk
import re
import ast

class dataLogger():

    def __init__(self, log_path, media_path):
        self.log_path = log_path
        self.media_path = media_path  # where to save the plot image

    def trim_right(self, word, trim):
        if word.endswith(trim):
            word = word[:-1*(len(trim))]
        return word

    def list_all_files(self):
        file_list = []
        for (dirpath, dirnames, filenames) in walk(self.log_path):
            file_list.extend(filenames)
            break
        #return file_list
        #file_list = [ re.sub('\.csv$', '', e) for e in file_list]
        file_list = [self.trim_right(e,".csv") for e in file_list]
        file_list.remove('logging_queue.txt')

        return file_list

    def fetch_file(self, file_name, filetype=None):
        name = file_name.strip('.json')
        full_name = os.path.join(self.log_path, name)
        full_name = "%s.csv" % (full_name)
        if not os.path.isfile(full_name):
            print "Data Log\t not found %s" % full_name
            return None
        else:
            raw = open(full_name, "rb").read()
            if (filetype == 'json'):
                data_list = []
                lines = raw.splitlines(True)
                for line in lines:
                    record = self.validate_line(line, name)
                    if record is not None:
                        data_list.append(record)
                return data_list
            return raw

    def validate_line(self, line, name):

        line = line.strip().split(',')
        if len(line) == 2:
            dict = {}
            dict['created_at'] = line[0]
            try:
                #convert string to float or int
                dict[name] = ast.literal_eval(line[1])
                return dict
            except:
                return None
        return None

    def validate_number(self, number):
        try:
            return ast.literal_eval(number)
        except:
            return None

    def delete_files(self, file_name):
        
        result = False
        list_file_name = file_name.split(",")
        
        for file_name in list_file_name:
            file_name = file_name.strip()
            full_name = os.path.join(self.log_path, file_name)
            full_name = "%s.csv" % (full_name)
            if "/" in file_name or not os.path.isfile(full_name):
                print "Data Log\t %s is invalid" % file_name
            else:
                os.remove(full_name)
                result = True
                print "Data Log\t %s deleted %s" % (file_name, result)
        return result

    def log(self, log_value, file_name):
        full_name = os.path.join(self.log_path, file_name + ".csv")
        #if not os.path.isfile(full_name):
        file = open(full_name, 'a')
        file.write("%s,%s\r\n" % (self.get_datetime_str(),log_value))
        file.close()

    def new_log_file(self, file_name):
        full_name = os.path.join(self.log_path, file_name + ".csv")
        if os.path.isfile(full_name):
            os.rename(full_name, os.path.join(self.log_path, file_name + "_" + str(datetime.datetime.now().strftime("%Y-%m-%d %H-%m-%S")) + ".csv"))

    def get_datetime_str(self):
        return str(datetime.datetime.now())

    def get_plot_image_path(self):
        return os.path.join(self.log_path, "plot.png" )

    def plot(self, n, file_list):
        ''' n = the number of latest data points to display '''

        print "plot"
        '''
        for file_name in file_list.split(","):
            print "plotting %s" % file_name

            full_name = os.path.join(self.log_path, file_name + ".csv")
            if not os.path.isfile(full_name):
                print "Plot file not found %s" % full_name
                return

            # 0 = plot all records
            if n == 0:
                data = [[i for i in line.strip().split(',')] for line in open(full_name).readlines()]
                data_date, data_value = map(list, zip(*(e for e in data)))
            else:
                data = self.get_last_n_lines(n, full_name)
                #data_date, data_value = map(list, zip(*(map(float, e.split()) for e in data.splitlines())))
                data_date, data_value = map(list, zip(*(e.split(',') for e in data.splitlines())))

            data_date = [datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S.%f') for d in data_date]
            data_value = [int(i) for i in data_value]

            hfmt = matplotlib.dates.DateFormatter('%m/%d %H:%M')

            plt.plot(data_date, data_value, label=file_name)


        plt.ylabel("value")
        plt.xlabel("time")
        plt.gca().xaxis.set_major_locator(matplotlib.dates.MinuteLocator())
        plt.gca().xaxis.set_major_formatter(hfmt)
        plt.xticks(rotation='vertical')
        plt.gca().set_ylim(bottom=0) # Y axis always starts at zero
        plt.subplots_adjust(bottom=.3)

        # Shrink current axis by 20%
        box = plt.gca().get_position()
        plt.gca().set_position([box.x0, box.y0, box.width * 0.8, box.height])
        # Put a legend to the right of the current axis
        plt.gca().legend(loc='center left', bbox_to_anchor=(1, 0.5))

        plt.savefig(os.path.join(self.media_path, "plot.png"))
        plt.clf() # clear the plot

        '''
        # for line in self.get_last_n_lines(data_points, full_name).split('\n'):
        #
        #     print line


    def get_last_n_lines(self, n, fileName):
        p = subprocess.Popen(['tail', '-n', str(n), fileName], stdout=subprocess.PIPE)
        s_output, s_input = p.communicate()
        return s_output


if __name__ == '__main__':
    dl = dataLogger("/home/pi/gogod/www/media/log", "/home/pi/gogod/www/media")
    print dl.delete_files('../field1_.csv,  field1_1.csv')
    #dl.plot(0, "switch,light")
