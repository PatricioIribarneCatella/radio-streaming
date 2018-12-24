#!/usr/bin/python3

import glob
import argparse
from os import kill, remove
from subprocess import Popen, signal

#
# Kills all the processes of the
# backend (antennas and routers)
#

def stop(file_path):

    with open(file_path, "r") as f:
        lines = f.readlines()
        for pid in lines:
            try:
                kill(int(pid), signal.SIGKILL)  
            except Exception:
                pass

    remove(file_path)

def main():

    for file_path in glob.glob("pids-antenna-*.store"):
        stop(file_path)

    for file_path in glob.glob("pids-router-*.store"):
        stop(file_path)

if __name__ == "__main__":

    main()

