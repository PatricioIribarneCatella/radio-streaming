import sys
import argparse
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from stations.station import RadialStation

def main(type_station, frequency):

    s = RadialStation(type_station, frequency)

    s.run()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                        description='Radio Streaming station',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
            "--type",
            help="RX or TX",
    )

    parser.add_argument(
            "--freq",
            help="Frequency of the form <ISO-COUNTRY>-<FREQ>"
    )

    args = parser.parse_args()

    main(args.type, args.freq)


