import argparse
import subprocess
from .monitor import *

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd",help="the program to monitor, use quotes if the program requires any options")
    parser.add_argument("-o","--output", default="monapp.data",help="base output name (default: monapp), the program appends the PID of the process it is monitoring")
    args = parser.parse_args()

    p = subprocess.Popen(args.cmd,shell=True)
    m = getMonitor(p.pid,args.output)
    p.wait()

if __name__ == '__main__':
    main()
