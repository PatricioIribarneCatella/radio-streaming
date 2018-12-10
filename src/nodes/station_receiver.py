import sys
import json
import argparse
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from stations.receiver import Receiver

def main(frequency, config):

    with open(config) as f:
        config_data = json.load(f)

    s = Receiver(frequency, config_data)

    s.run()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                        description='Radio receiver',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)


    parser.add_argument(
            "--freq",
            help="Frequency of the form <ISO-COUNTRY>-<FREQ>"
    )

    parser.add_argument(
            "--config",
            help="Topology configuration"
    )

    args = parser.parse_args()

    main(args.freq, args.config)


