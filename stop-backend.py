#!/usr/bin/python3

import argparse
from subprocess import Popen, signal
from os import kill

import json
#
# Runs the anthena (and its replicas) that
# belongs to a certain country 
#



def stop(file):

    with open(file, "r") as f:
        for line in f.readlines():
            _, pid = line.split(" ")
            try:
                kill(int(pid), signal.SIGTERM)  
            except Exception:
                pass

def main(config):
    stop(config)
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    description='Radio Streaming backend(anthena and routers) stopper script. Assumes the backend is running locally',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--pids",
        help="The file where the pids are stored",
        default="pids.store"
    )

    args = parser.parse_args()

    main(args.pids)

