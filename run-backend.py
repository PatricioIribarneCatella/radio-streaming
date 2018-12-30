#!/usr/bin/python3

import json
import argparse
from os import path
from subprocess import Popen

#
# Runs the antenna (and its replicas)
# for a given topology and scenario
#
# Example: AR and BR with 3 nodes each,
#   and 3 international routers
#

PYTHON = "python3"
NODES_DIR = path.join(path.dirname(__file__), "src/nodes/")

def run(config):

    pids = []

    with open(config) as f:
        config_data = json.load(f)

    # Antennas
    total_retransmitters = config_data['retransmitter_endpoints']

    for country in total_retransmitters:
        
        country_retransmitters = total_retransmitters[country]
        
        for node_number in range(len(country_retransmitters)):
            p = Popen([PYTHON,
                   NODES_DIR + "antenna.py",
                   "--country={}".format(country),
                   "--aid={}".format(node_number),
                   "--config={}".format(config)])
            pids.append(("antenna-{}-{}".format(country, node_number), p.pid))

    # Routers
    routers = config_data['routers_endpoints']

    for router_number in range(len(routers)):
        p = Popen([PYTHON,
                   NODES_DIR + "router.py",
                   "--node={}".format(router_number),
                   "--config={}".format(config)])
        pids.append(("router-{}".format(router_number), p.pid))

    return pids

def store(pids):

    for pid in pids:
        with open("pids-{}.store".format(pid[0]), "a") as f:
            f.write(str(pid[1]) + "\n")

def main(config):

    pids = run(config)

    store(pids)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    description='Radio Streaming backend(retransmitters and routers) run script',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--config",
        help="The topology configuration file. Must be in JSON format",
        default="config.json"
    )

    args = parser.parse_args()

    main(args.config)

