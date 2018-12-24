import sys
import json
import argparse
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from rebroadcast.rxtx import Antenna

def main(country, aid, config):

    with open(config) as f:
        config_data = json.load(f)

    a = Antenna(country, aid, config_data)

    a.run()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                        description='Radio Streaming RXTX Antenna',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
            "--country",
            help="Country of the form: <ISO-COUNTRY>"
    )


    parser.add_argument(
            "--config",
            help="Topology configuration",
    )

    parser.add_argument(
            "--aid",
            type=int,
            help="Antenna id"
    )

    args = parser.parse_args()

    main(args.country, args.aid, args.config)


