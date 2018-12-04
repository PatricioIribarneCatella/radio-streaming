import sys
import argparse
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from rebroadcast.rxtx import Anthena

def main(country, nodes):

    a = Anthena(country, nodes)

    a.run()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                        description='Radio Streaming RXTX anthena',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
            "--country",
            help="Country of the form: <ISO-COUNTRY>"
    )

    parser.add_argument(
            "--nodes",
            help="Number of replica nodes",
            default=2
    )

    args = parser.parse_args()

    main(args.country, nodes)


