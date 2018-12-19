#!/usr/bin/python3

import argparse
from subprocess import Popen
from os import path
import json
#
# Runs the anthena (and its replicas) that
# belongs to a certain country 
#

PYTHON = "python"
NODES_DIR = path.join(path.dirname(__file__), "src/nodes/")

def run(config):
    pids = []

    with open(config) as f:
        config_data = json.load(f)

    total_retransmitters = config_data['retransmitter_endpoints']

    for country in total_retransmitters:
        country_retransmitters = total_retransmitters[country]
        for node_number in range(len(country_retransmitters)):
            p = Popen([PYTHON,
                   NODES_DIR + "anthena.py",
                   "--country={}".format(country),
                   "--aid={}".format(node_number),
                   "--config={}".format(config)])
            pids.append("Anthena-{}-{} {}".format(country, node_number, p.pid))

    routers = config_data['routers_endpoints']

    for router_number in range(len(routers)):
        p = Popen([PYTHON,
                   NODES_DIR + "router.py",
                   "--node={}".format(router_number),
                   "--config={}".format(config)])
        pids.append("Router-{} {}".format(router_number, p.pid))

    return pids

def store(pids):

    with open("pids.store", "w+") as f:
        for pid in pids:
            f.write(str(pid) + "\n")

def main(config):

    pids = run(config)

    store(pids)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    description='Radio Streaming backend(retransmitters and routers) run script',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--config",
        help="The topology configuration file. Must be in json format",
        default="config.json"
    )

    args = parser.parse_args()

    main(args.config)

