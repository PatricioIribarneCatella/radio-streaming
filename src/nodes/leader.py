import sys
import json
import argparse
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from rebroadcast.leader import LeaderCoordinator

def main(country, nodes, aid, config):

    with open(config) as f:
        config_data = json.load(f)

    l = LeaderCoordinator(country, nodes, aid, config_data)

    l.run()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                        description='Radio Streaming Leader tester',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
            "--country",
            help="Country of the form: <ISO-COUNTRY>"
    )

    parser.add_argument(
            "--nodes",
            type=int,
            help="Number of replica nodes",
            default=2
    )

    parser.add_argument(
            "--config",
            help="Topology configuration",
    )

    parser.add_argument(
            "--aid",
            type=int,
            help="Anthena id"
    )

    args = parser.parse_args()

    main(args.country, args.nodes, args.aid, args.config)


