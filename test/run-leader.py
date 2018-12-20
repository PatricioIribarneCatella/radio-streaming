#!/usr/bin/python3

import argparse
from subprocess import Popen

#
# Leader tester script
#
# Runs a leader node that
# belongs to a certain country 
#

PYTHON = "python3"
NODES_DIR = "src/nodes/"
CONFIG_DIR = "src/config.json"

def run(country, aid, antennas):

    p = Popen([PYTHON,
               NODES_DIR + "leader.py",
               "--config={}".format(CONFIG_DIR),
               "--country={}".format(country),
               "--nodes={}".format(antennas),
               "--aid={}".format(aid)])

    return p.pid

def store(pid, aid, country):

    with open("pids-{}-{}.store".format(country, aid), "a") as f:
        f.write(str(pid) + "\n")

def main(country, aid, antennas):

    pid = run(country, aid, antennas)

    store(pid, aid, country)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    description='Radio Streaming antennas run script',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--country",
        help="The country the antennas belong to"
    )

    parser.add_argument(
        "--aid",
        help="The antenna id",
        type=int
    )

    parser.add_argument(
        "--antennas",
        default=1,
        type=int,
        help="Number of antennas in that country"
    )

    args = parser.parse_args()

    main(args.country, args.aid, args.antennas)

