#!/usr/bin/python3

import argparse
from subprocess import Popen

#
# Runs an antenna that
# belongs to a certain country 
#

PYTHON = "python3"
NODES_DIR = "src/nodes/"
CONFIG_DIR = "config.json"

def run(country, aid):

    p = Popen([PYTHON,
               NODES_DIR + "anthena.py",
               "--config={}".format(CONFIG_DIR),
               "--country={}".format(country),
               "--aid={}".format(aid)])

    return p.pid

def store(pid, aid, country):

    with open("pids-antenna-{}-{}.store".format(country, aid), "a") as f:
        f.write(str(pid) + "\n")

def main(country, aid):

    pid = run(country, aid)

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

    args = parser.parse_args()

    main(args.country, args.aid)

