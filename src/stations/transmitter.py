import sys
from os import path
from time import sleep
from multiprocessing import Process

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import middleware.constants as cons
import rebroadcast.messages as m
from middleware.channels import DataInterNode, InterProcess, DataInterProcess, Poller

class Transmitter(Process):

    def __init__(self, country, frequency_code, config):

        self.config = config
        self.country = country
        self.frequency_code = frequency_code

        super(Transmitter, self).__init__()
        
    def _initialize(self):

        self.output = DataInterNode(cons.PUSH)

        self.data = DataInterProcess(cons.PULL)
        self.data.connect("station-sender-data-{}".format(
                            self.frequency_code))

        self.signal = InterProcess(cons.PULL)
        self.signal.connect("station-sender-signal-{}".format(
                            self.frequency_code))

        self.poller = Poller([self.signal,
                              self.data])

    def _wait_for_leader(self):

        # Wait for signal of listener module
        # which means a call to recv() on signal channel

        msg, nid = self.signal.recv()
        leader = int(nid)

        output_endpoint = self.config["retransmitter_endpoints"][self.country][leader]["input"]
        self.output.connect(output_endpoint)

    def _transmit(self):

        while True:

            socks = self.poller.poll(None)

            for s, poll_type in socks:

                # receive messages from:
                #   data -> forward to antenna (output channel)
                #   signal -> change leader and connect to it
                mtype, msg = s.recv()
                
                if mtype == m.NEW_DATA:
                    msg = {"freq": msg["freq"],
                           "data": msg["data"]}
                    self.output.send(msg)
                elif mtype == m.LEADER_DOWN:
                    self._wait_for_leader()

    def _close(self):
        
        self.output.close()
        self.signal.close()
        self.data.close()

    def run(self):
        
        self._initialize()

        self._wait_for_leader()

        self._transmit()

        self._close()


