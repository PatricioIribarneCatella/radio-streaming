import sys
from os import path
from multiprocessing import Process

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import rebroadcast.messages as m
import middleware.constants as cons
from stations.utils import search_leader
from middleware.channels import TopicInterNode, InterProcess, TimeOut

class SenderListener(Process):

    def __init__(self, country, frequency, config):

        self.frequency = frequency
        self.country = country
        self.config = config
        self.antennas = len(config["retransmitter_endpoints"][self.country])

        super(SenderListener, self).__init__()

    def _initialize(self):

        self.listener = TopicInterNode([""])
        
        self.transmitter = InterProcess(cons.PUSH)
        self.transmitter.bind("station-sender-signal-{}".format(
                                self.frequency))

        self._look_for_leader()

    def _look_for_leader(self):

        leader = search_leader(self.country, self.config)

        # The leader is up
        lid = leader["node"]
        self.listener.connect(self.config["retransmitter_endpoints"][self.country][int(lid)]["alive"]["connect"],
                                timeout=cons.TIMEOUT)
        
        # Notify the transmitter
        # which node is the leader
        self.transmitter.send({"mtype": m.LEADER, "node": lid})

    def run(self):

        # Listen for leader's heartbeats
        # If no response from leader,
        # send FAIL signal to transmitter
        # module to stop sending messages
        # and then ask for the new leader.
        # Finally notify the transmitter.

        self._initialize()

        while True:

            try:
                self.listener.recv()
            except TimeOut:
                print("Sender listener: Leader down")
                self.transmitter.send({"mtype": m.LEADER_DOWN, "node": 0})
                self._look_for_leader()

        self.listener.close()


