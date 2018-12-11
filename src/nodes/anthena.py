import sys
import json
import argparse
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from rebroadcast.transmission import Retransmitter

def main(country, node, config):

    with open(config) as f:
        config_data = json.load(f)

    r = Retransmitter(country, int(node), config_data)

    r.run()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                        description='Radio Streaming RXTX anthena',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
            "--country",
            help="Country of the form: <ISO-COUNTRY>"
    )

    parser.add_argument(
            "--node",
            help="Number of node"
    )

    parser.add_argument(
            "--config",
            help="Topology configuration",
    )

    args = parser.parse_args()

    main(args.country, args.node, args.config)


