#!/usr/bin/python3

import argparse
from subprocess import Popen

#
# Runs the antenna (and its replicas) that
# belongs to a certain country 
#

PYTHON = "python3"
NODES_DIR = "src/nodes/"
CONFIG_DIR = "src/config.json"

def run(country, antennas):

    pids = []

    for aid in range(1, antennas + 1):
        p = Popen([PYTHON,
                   NODES_DIR + "anthena.py",
                   "--config={}".format(CONFIG_DIR),
                   "--country={}".format(country),
                   "--nodes={}".format(antennas),
                   "--aid={}".format(aid)])
        pids.append(p.pid)

    return pids

def store(pids):

    with open("pids.store", "w+") as f:
        for pid in pids:
            f.write(str(pid) + "\n")

def main(country, antennas):

    pids = run(country, antennas)

    store(pids)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    description='Radio Streaming antennas run script',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--country",
        help="The country the antennas belong to"
    )

    parser.add_argument(
        "--antennas",
        default=1,
        type=int,
        help="Number of antennas in that country"
    )

    args = parser.parse_args()

    main(args.country, args.antennas)

