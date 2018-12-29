#!/usr/bin/python3

import signal
import argparse
from os import kill, remove

#
# Kills all the processes
# that belongs to a certain node (Router)
# of in a given country
#

def main(aid):

    file_path = "pids-router-{}.store".format(aid)

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
                    description='Radio Streaming routers kill script',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--rid",
        help="The router id",
        type=int
    )

    args = parser.parse_args()

    main(args.rid)


