#!/usr/bin/python3

import sys
from os import path
from time import sleep

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from src.audio.player import AudioPlayer
from src.audio.reader import AudioReader

#
# Audio (reader/player) test script
#

MUSIC = "../clasica.wav"

def main():

    p = AudioPlayer()
    r = AudioReader(MUSIC)

    for chunk in r.chunks():
        p.play(chunk)

    p.close()

if __name__ == "__main__":
    main()


