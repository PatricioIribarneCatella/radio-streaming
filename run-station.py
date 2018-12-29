#!/usr/bin/python3

import argparse
from subprocess import Popen

#
# Runs a radial station type with
# a certain frequency
#

PYTHON = "python3"
NODES_DIR = "src/nodes/"
CONFIG = "config.json"

def run_sender(frequency, input_file, config):

    pids = []

    p = Popen([PYTHON,
               NODES_DIR + "sender.py",
               "--freq={}".format(frequency),
               "--input={}".format(input_file),
               "--config={}".format(config)])
    pids.append(p.pid)

    return pids

def run_receiver(frequency, country, config):

    pids = []

    p = Popen([PYTHON,
               NODES_DIR + "receiver.py",
               "--freq={}".format(frequency),
               "--country={}".format(country),
               "--config={}".format(config)])
    pids.append(p.pid)

    return pids

def store(pids, type_station, freq):

    with open("pids-stations-{}-{}.store".format(type_station, freq), "a") as f:
        for pid in pids:
            f.write(str(pid) + "\n")

def main(type_station, frequency, country, input_file):

    pids = []

    if type_station == "TX":
        pids = run_sender(frequency, input_file, config)
    elif type_station == "RX":
        pids = run_receiver(frequency, country, config)
    else:
        print("Bad station type given: Just RX | TX allowed")
        return

    store(pids, type_station, frequency)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    description='Radio Streaming station run script',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--type",
        help="Station type: RX or TX"
    )

    parser.add_argument(
        "--country",
        default="AR"
        help="Country in which the station is running"
    )

    parser.add_argument(
        "--input",
        default="clasica.wav",
        help="The music to be reproduced by the transmitter"
    )

    parser.add_argument(
        "--freq",
        help="Frequency of the form <ISO-COUNTRY>-<FREQ>"
    )

    args = parser.parse_args()

    main(args.type, args.freq, args.country, args.input)


