#!/usr/bin/python3

import signal
import argparse
from os import kill, remove

#
# Kills all the processes
# that belongs to a certain node of
# in a given country
#

def main(country, aid):

    file_path = "pids-{}-{}.store".format(country, aid)

    with open(file_path) as f:
        
        lines = f.readlines()

        for pid in lines:
            try:
                    
                kill(int(pid), signal.SIGKILL)
            except Exception:
                pass
    # Delete file so when the node
    # starts again it could have its
    # file clean
    remove(file_path)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    description='Radio Streaming antennas kill script',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--country",
        help="The country the antennas belong to"
    )

    parser.add_argument(
        "--aid",
        help="The antenna id",
        type=int
    )

    args = parser.parse_args()

    main(args.country, args.aid)


