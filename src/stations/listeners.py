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
        self.listener_endpoint = None

        super(SenderListener, self).__init__()

    def _initialize(self):

        self.listener = TopicInterNode([""])
        
        self.transmitter = InterProcess(cons.PUSH)
        self.transmitter.bind("station-sender-signal-{}".format(
                                self.frequency))

        self._look_for_leader()

    def _look_for_leader(self):

        lid = search_leader(self.country, self.config)

        print("Listener (sender)-{}: elected leader is: {}".format(
                    self.frequency, lid))

        # The leader is up
        self.listener.disconnect(self.listener_endpoint)
        self.listener_endpoint = self.config["retransmitter_endpoints"][self.country][lid]["alive"]["connect"]
        self.listener.connect(self.listener_endpoint, timeout=cons.TIMEOUT)
        
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
                mtype, node = self.listener.recv()
                if node["state"] == m.NOT_LEADER:
                    self.transmitter.send({"mtype": m.LEADER_UP, "node": 0})
                    self._look_for_leader()
            except TimeOut:
                print("Sender listener: Leader down")
                self.transmitter.send({"mtype": m.LEADER_DOWN, "node": 0})
                self._look_for_leader()

        self.listener.close()
        self.transmitter.close()


class ReceiverListener(Process):

    def __init__(self, country, frequency, config):
        
        self.config = config
        self.frequency = frequency
        self.country = country
        self.listener_endpoint = None

        super(ReceiverListener, self).__init__()

    def _initialize(self):

        self.listener = TopicInterNode([""])
        
        self.receiver = InterProcess(cons.PUSH)
        self.receiver.bind("station-receiver-signal-{}".format(
                                self.frequency))

        self._look_for_leader()

    def _look_for_leader(self):

        lid = search_leader(self.country, self.config)

        print("Listener (receiver)-{}: elected leader is: {}".format(
                    self.frequency, lid))

        # The leader is up
        self.listener.disconnect(self.listener_endpoint)
        self.listener_endpoint = self.config["retransmitter_endpoints"][self.country][lid]["alive"]["connect"]
        self.listener.connect(self.listener_endpoint, timeout=cons.TIMEOUT)
        
        # Notify the receiver
        # which node is the leader
        self.receiver.send({"mtype": m.LEADER, "node": lid})

    def run(self):
        
        # Listen for leader's heartbeats
        # If no response from leader,
        # send FAIL signal to receiver
        # module and look for a new leader.
        # Finally notify the receiver about
        # the change.

        self._initialize()

        while True:

            try:
                mtype, node = self.listener.recv()
                if node["state"] == m.NOT_LEADER:
                    self.receiver.send({"mtype": m.LEADER_UP, "node": 0})
                    self._look_for_leader()
            except TimeOut:
                print("Receiver listener: Leader down")
                self.receiver.send({"mtype": m.LEADER_DOWN, "node": 0})
                self._look_for_leader()

        self.listener.close()
        self.receiver.close()


