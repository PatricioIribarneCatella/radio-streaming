#!/usr/bin/python3

import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import src.middleware.constants as cons
from src.middleware.channels import DataInterNode
from src.audio.player import AudioPlayer

#
# Audio RECEIVER test script
#

def main():

    p = AudioPlayer()

    socket = DataInterNode(cons.PULL)
    socket.bind("0.0.0.0:8888")

    while True:
        freq, chunk = socket.recv()
        print("freq: {}".format(freq))
        p.play(chunk)

    p.close()

if __name__ == "__main__":
    main()


