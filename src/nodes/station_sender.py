import re
import sys
import json
import argparse
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from stations.sender import Sender

def main(frequency, input_file, config):

    match = re.match(r'^(\w{2,3})-\d{2,3}\.\d$', frequency)

    if match is None:
        print("Bad frequency format given. Must be <ISO-COUNTRY>-<FREQ>")
        return

    country = match.group(1)

    with open(config) as f:
        config_data = json.load(f)

    s = Sender(frequency, country, input_file, config_data)

    s.run()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                        description='Radio transmitter',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)


    parser.add_argument(
            "--freq",
            help="Frequency of the form <ISO-COUNTRY>-<FREQ>"
    )

    parser.add_argument(
            "--input",
            help="WAV input file"
    )

    parser.add_argument(
            "--config",
            help="Topology configuration"
    )

    args = parser.parse_args()

    main(args.freq, args.input, args.config)


