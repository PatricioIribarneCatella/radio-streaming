#!/usr/bin/python3

import json
import argparse

FILE_OUTPUT = "config.json"

def generate_config(antennas_spec, routers):

    config = {}

    RETRANSMITTERS = "retransmitter_endpoints"
    ROUTERS = "routers_endpoints"

    IP_CONNECT = "127.0.0.1"
    IP_BIND = "0.0.0.0"

    OUTPUT_PORT = 4000
    INPUT_PORT = 3000
    ADMIN_PORT = 2000

    LEADER_PORT = 5000
    ALIVE_PORT = 6000
    QUERY_PORT = 7000

    ROUTER_OUTPUT_PORT = 8000
    ROUTER_INPUT_PORT = 9000
    ROUTER_HEARTBEAT_PORT = 10000

    config[RETRANSMITTERS] = {}
    config[ROUTERS] = []

    j = 0
    
    for iso in antennas_spec:
        
        config[RETRANSMITTERS][iso] = []

        for i in range(0, antennas_spec[iso]):
            node = {
                "output": "{}:{}".format(IP_CONNECT, OUTPUT_PORT + j),
                "input": "{}:{}".format(IP_CONNECT, INPUT_PORT + j),
                "admin": "{}:{}".format(IP_CONNECT, ADMIN_PORT + j),
                "connect": {
                    "ip": IP_CONNECT,
                    "port": LEADER_PORT + j
                },
                "bind": {
                    "ip": IP_BIND,
                    "port": LEADER_PORT + j
                },
                "alive": {
                    "bind": {
                        "ip": IP_BIND,
                        "port": ALIVE_PORT + j
                    },
                    "connect": {
                        "ip": IP_CONNECT,
                        "port": ALIVE_PORT + j
                    }
                },
                "query-leader": {
                    "bind": {
                        "ip": IP_BIND,
                        "port": QUERY_PORT + j
                    },
                    "connect": {
                        "ip": IP_CONNECT,
                        "port": QUERY_PORT + j
                    }
                }
            }

            j += 1
            config[RETRANSMITTERS][iso].append(node)

    for r in range(0, routers):

        router = {
            "output": "{}:{}".format(IP_CONNECT, ROUTER_OUTPUT_PORT + r),
            "input": "{}:{}".format(IP_CONNECT, ROUTER_INPUT_PORT + r),
            "heartbeat": {
                "bind": {
                    "ip": IP_BIND,
                    "port": ROUTER_HEARTBEAT_PORT + r
                },
                "connect": {
                    "ip": IP_CONNECT,
                    "port": ROUTER_HEARTBEAT_PORT + r
                }
            }
        }

        config[ROUTERS].append(router)

    return config

def main(antennas, routers, output):

    antennas = antennas.strip("[]").split(",")

    spec = dict()

    for country in antennas:
        iso, nodes = country.split(":")
        spec[iso] = int(nodes)

    config = generate_config(spec, routers)

    with open(output, "w") as f:
        json.dump(config, f, indent=4)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    description='Radio Streaming config generator script',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--antennas",
        help="Specification antennas topology"
    )

    parser.add_argument(
        "--routers",
        type=int,
        help="Number of routers"
    )

    parser.add_argument(
        "--output",
        default=FILE_OUTPUT,
        help="File output name"
    )

    args = parser.parse_args()

    main(args.antennas, args.routers, args.output)

