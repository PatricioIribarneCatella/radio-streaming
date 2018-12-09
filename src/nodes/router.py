import sys
import json
import argparse
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from stations.router import Router

def main(config):

    with open(config) as f:
        config_data = json.load(f)

    r = Router(config_data)

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

    args = parser.parse_args()

    main(args.config)


