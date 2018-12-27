#!/usr/bin/python3

import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import src.middleware.constants as cons
from src.middleware.channels import DataInterNode
from src.audio.reader import AudioReader

#
# Audio SENDER test script
#

MUSIC = "../clasica.wav"

def main():

    r = AudioReader(MUSIC)

    socket = DataInterNode(cons.PUSH)
    socket.connect("localhost:8888")

    for chunk in r.chunks():
        socket.send({"freq": "AR-101.1", "data": chunk})
        print("Chunk sended")

    socket.close()

if __name__ == "__main__":
    main()


