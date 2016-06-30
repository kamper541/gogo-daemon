#!/usr/bin/python
import subprocess
import sys


# source = open(filename, 'r').read() + '\n'
# compile(source, filename, 'exec')

def verify(filename):
    cmd = "python -m py_compile %s" % filename
    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    print err
    return err == ""


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        print filename
        print verify(filename)
