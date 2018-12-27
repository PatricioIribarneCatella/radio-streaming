import re
import sys
import json
import argparse
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from stations.receivers import Receiver
from stations.receivers import InternationalReceiver

def main(country, frequency, config):

    match = re.match(r'^(\w{2,3})-\d{2,3}\.\d$', frequency)

    if match is None:
        print("Bad frequency format given. Must be <ISO-COUNTRY>-<FREQ>")
        return

    freq_country = match.group(1)

    with open(config) as f:
        config_data = json.load(f)

    if country == freq_country:
        r = Receiver(country, frequency, config_data)
        r.run()
    else:
        ir = InternationalReceiver(country, frequency,
                                   freq_country, config)
        ir.run()

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

    parser.add_argument(
            "--country",
            help="Topology configuration",
            default=None
    )

    args = parser.parse_args()

    main(args.country, args.freq, args.config)


