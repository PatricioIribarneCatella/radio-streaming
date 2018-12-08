import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from transmission import Retransmitter
from leader import LeaderElection, LeaderTester
from listener import TestListener

class Anthena(object):

    def __init__(self, country, nodes, config):

        self.country = country
        self.nodes = nodes
        self.config = config

    def run(self):

        print("Anthena running")

        r = Retransmitter(self.config)
        r.start()

        le = LeaderElection(self.config)
        le.start()

        lt = LeaderTester(self.config)
        lt.start()

        l = TestListener(self.config)
        l.start()

