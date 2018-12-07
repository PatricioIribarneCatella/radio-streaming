import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from transmission import Retransmitter
from leader import LeaderElection, LeaderTester
from listener import TestListener

class Anthena(object):

    def __init__(self, country, nodes):

        self.country = country
        self.nodes = nodes

    def run(self):

        print("Anthena running")

        r = Retransmitter()
        r.start()

        le = LeaderElection()
        le.start()

        lt = LeaderTester()
        lt.start()

        l = TestListener()
        l.start()

