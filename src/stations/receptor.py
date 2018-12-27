import sys
from os import path
from multiprocessing import Process

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import rebroadcast.messages as m
import middleware.constants as cons
from stations.utils import search_leader
from middleware.channels import Poller, InterNode, InterProcess, DataInterProcess, DataTopicInterNode

class Receptor(Process):

    def __init__(self, country, frequency, config):

        self.country = country
        self.frequency = frequency
        self.config = config

        super(Receptor, self).__init__()

    def _initialize(self):

        self.input = DataTopicInterNode([self.frequency])

        self.data = DataInterProcess(cons.PUSH)
        self.data.connect("station-receiver-data-{}".format(
                            self.frequency))

        self.signal = InterProcess(cons.PULL)
        self.signal.connect("station-receiver-signal-{}".format(
                            self.frequency))

        self.poller = Poller([self.signal,
                              self.input])

    def _wait_for_leader(self):

        # Wait for signal of listener module
        # which means a call to recv() on signal channel

        msg, nid = self.signal.recv()
        leader = int(nid)

        # Connects to leader
        # and sends a 'listening request'
        # to register the international 
        # frequency (for listening) in the new node
        admin = InterNode(cons.REQ)
        admin.connect(self.config["retransmitter_endpoints"][self.country][leader]["admin"])

        admin.send({"type": m.LISTEN_OTHER_COUNTRY,
                    "frequency": self.frequency})

        admin.recv()
        admin.close()

        input_endpoint = self.config["retransmitter_endpoints"][self.country][leader]["output"]
        self.input.connect(input_endpoint)

    def _receive(self):

        while True:

            socks = self.poller.poll(None)

            for s, poll_type in socks:
                
                # receive messages from:
                #   data -> from the antenna (intput channel)
                #       send it to main process via 'data channel'
                #   signal -> change leader and connect to it
                first, chunk = s.recv()

                if first == m.LEADER_DOWN:
                    self._wait_for_leader()
                else:
                    msg = {"mtype": m.NEW_DATA,
                           "freq": self.frequency,
                           "data": chunk}
                    self.data.send(msg)

    def _unsubscribe(self):

        lid = search_leader(self.country, self.config)

        admin = InterNode(cons.REQ)
        admin.connect(self.config["retransmitter_endpoints"][self.country][lid]["admin"])

        admin.send({"type": m.STOP_LISTEN_OTHER_COUNTRY,
                    "frequency": self.frequency})

        admin.recv()
        admin.close()

    def _close(self):

        self.input.close()
        self.signal.close()
        self.data.close()

        self._unsubscribe()

    def run(self):
        
        self._initialize()

        self._wait_for_leader()

        self._receive()

        self._close()



