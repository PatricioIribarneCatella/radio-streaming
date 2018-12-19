import os
import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from rebroadcast.leader import LeaderCoordinator
from rebroadcast.transmission import Retransmitter

class Antenna(object):

    def __init__(self, country, aid, config):

        self.country = country
        self.config = config
        self.aid = aid
        super(Antenna, self).__init__()

    def run(self):

        print("Antenna running. Country: {}, id: {}".format(
                    self.country, self.aid))

        rt = Retransmitter(self.country, self.aid, self.config)
        rt.start()

        lc = LeaderCoordinator(self.country, self.aid, self.config)
        lc.start()

        print("Antenna module down")


