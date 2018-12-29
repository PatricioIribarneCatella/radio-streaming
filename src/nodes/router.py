import sys
import json
import argparse
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from stations.router import Router

def main(node, config):

    with open(config) as f:
        config_data = json.load(f)

    r = Router(node, config_data)

    r.run()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                        description='Router ',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    
    parser.add_argument(
            "--config",
            help="Topology configuration",
            default='config.json'
    )

    parser.add_argument(
            "--node",
            type=int,
            help="Number of node"
    )

    args = parser.parse_args()

    main(args.node, args.config)


