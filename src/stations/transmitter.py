import sys
import signal
from os import path
from time import sleep
from multiprocessing import Process

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import middleware.constants as cons
import rebroadcast.messages as m
from middleware.channels import DataInterNode, InterNode, InterProcess, DataInterProcess, Poller

class Transmitter(Process):

    def __init__(self, country, frequency_code, config):

        self.config = config
        self.country = country
        self.frequency_code = frequency_code
        self.output_endpoint = None

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

    def _wait_for_leader(self, first_time):

        # Wait for signal of listener module
        # which means a call to recv() on signal channel

        msg, nid = self.signal.recv()
        leader = int(nid)

        if not first_time:
            # Connects to leader
            # and sends a 'transmitting request'
            # to register the frequency in the new node
            admin = InterNode(cons.REQ)
            admin.connect(self.config["retransmitter_endpoints"][self.country][leader]["admin"])

            admin.send({"type": m.START_TRANSMITTING,
                        "frequency": self.frequency_code})

            admin.recv()
            admin.close()

        self.output.disconnect(self.output_endpoint)
        self.output_endpoint = self.config["retransmitter_endpoints"][self.country][leader]["input"]
        self.output.connect(self.output_endpoint)

    def _transmit(self):

        try:
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
                    elif mtype == m.LEADER_DOWN or mtype == m.LEADER_UP:
                        self._wait_for_leader(False)

        except KeyboardInterrupt:
            pass

    def _close(self):
        
        self.output.close()
        self.signal.close()
        self.data.close()

    def run(self):
        
        self._initialize()

        self._wait_for_leader(True)

        self._transmit()

        self._close()


