#!/usr/bin/python3

import argparse
from subprocess import Popen

#
# Runs a radial station type with
# a certain frequency
#

PYTHON = "python3"
NODES_DIR = "src/nodes/"

def run(country, anthenas):

    pids = []

    p = Popen([PYTHON,
               NODES_DIR + "station.py",
               "--type={}".format(type_station),
               "--freq={}".format(frequency)])
    pids.append(p.pid)

    return pids

def store(pids):

    with open("pids-stations.store", "a") as f:
        for pid in pids:
            f.write(str(pid) + "\n")

def main(type_station, frequency):

    pids = run(type_station, frequency)

    store(pids)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    description='Radio Streaming station run script',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--type",
        help="Station type: RX or TX"
    )

    parser.add_argument(
        "--freq",
        help="Frequency of the form <ISO-COUNTRY>-<FREQ>"
    )

    args = parser.parse_args()

    main(args.type, args.freq)

