#!/usr/bin/python3

import argparse
from subprocess import Popen

#
# Runs a router
#

PYTHON = "python3"
NODES_DIR = "src/nodes/"

def run(rid, config):

    p = Popen([PYTHON,
               NODES_DIR + "router.py",
               "--config={}".format(config),
               "--node={}".format(rid)])

    return p.pid

def store(pid, rid):

    with open("pids-router-{}.store".format(rid), "a") as f:
        f.write(str(pid) + "\n")

def main(rid, config):

    pid = run(rid, config)

    store(pid, rid)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    description='Radio Streaming router run script',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--rid",
        help="The router id",
        type=int
    )

    parser.add_argument(
        "--config",
        help="Configuration file",
        default="config.json"
    )

    args = parser.parse_args()

    main(args.rid, args.config)

