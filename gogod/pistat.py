# Original code from uCast (CPU load, Memory) and http://rollcode.com/ (Temperature)
# Modified by Arnan (Roger) Sipitakiat

import re, time, sys
import commands

class PiStats(object):
  def __init__(self):
    self.total_memory = None
    self.free_memory = None
    self.cached_memory = None
    self.lastCPUInfo = {'total':0, 'active':0}
    self.currentCPUInfo = {'total':0, 'active':0}
    self.temp_in_celsius = None

  def calculate_cpu_percentage(self):
    total_diff = self.currentCPUInfo['total'] - self.lastCPUInfo['total']
    active_diff = self.currentCPUInfo['active'] - self.lastCPUInfo['active']

    # this happens sometimes
    if active_diff == 0:
        active_diff = 1

    return round(float(active_diff) / float(total_diff), 3) * 100.00

  def update_stats(self):
    # Read memory usage from /proc/meminfo
    with open('/proc/meminfo', 'r') as mem_file:
      # Remove the text description, kB, and whitespace before
      # turning file lines into an int
      for i, line in enumerate(mem_file):
        if i == 0: # Total line
          self.total_memory = int(line.strip("MemTotal: \tkB\n")) / 1024
        elif i == 1: # Free line
          self.free_memory = int(line.strip("MemFree: \tkB\n")) / 1024
        elif line.find("Cached:") == 0: # Cached line
          self.cached_memory = int(line.strip("Cached: \tkB\n")) / 1024

    self.lastCPUInfo['total'] = self.currentCPUInfo['total']
    self.lastCPUInfo['active'] = self.currentCPUInfo['active']
    self.currentCPUInfo['total'] = 0
    with open('/proc/stat', 'r') as cpu_file:
      for i, line in enumerate(cpu_file):
        if i == 0:
          cpuStats = re.findall('([0-9]+)', line.strip())
          self.currentCPUInfo['idle'] = int(cpuStats[3]) + int(cpuStats[4])
          for t in cpuStats:
            self.currentCPUInfo['total'] += int(t)

          self.currentCPUInfo['active'] = self.currentCPUInfo['total'] - self.currentCPUInfo['idle']
          self.currentCPUInfo['percent'] = self.calculate_cpu_percentage()

    self.temp_in_celsius = self.get_cpu_temp()


  def get_memory_info(self):
    # In linux the cached memory is available for program use so we'll
    # include it in the free amount when calculating the usage percent
    used_val = (self.total_memory - self.free_memory)
    free_val = (self.free_memory)
    percent_val = float(used_val - self.cached_memory) / float(self.total_memory)
    return {'total': self.total_memory, 'cached': self.cached_memory,  'used': used_val, 'free': free_val, 'percent': round(percent_val, 3) * 100.00 }


  def get_cpu_temp(self):
    tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
    cpu_temp = tempFile.read()
    tempFile.close()
    return float(cpu_temp)/1000
    # Uncomment the next line if you want the temp in Fahrenheit
    #return float(1.8*cpu_temp)+32

  def get_cpu_info(self):
    return self.currentCPUInfo

if __name__ == '__main__':
    stats = PiStats()
    stats.update_stats()
    meminfo = stats.get_memory_info()

    print "total\tused\tfree\tcached"
    print "%i\t%i\t%i\t%i"%(meminfo['total'],meminfo['used'],meminfo['free'],meminfo['cached'])
    print "Memory Usage:\t%i%%"%(meminfo['percent'])
    print "\n"

    try:
      while True:
        stats.update_stats()
        cpu_info = stats.get_cpu_info()
        meminfo = stats.get_memory_info()

        print "CPU Load:\t%i%%"%(cpu_info['percent'])
        print "Memory used:\t%i%%"%(meminfo['percent'])
        print "CPU Temperature:\t%i C"%(stats.temp_in_celsius)
        time.sleep(2);

    except KeyboardInterrupt:
      print "Exiting.\n"
      sys.exit(0)