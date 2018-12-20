import sys
import time
import signal
from os import path
from multiprocessing import Process

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import rebroadcast.messages as m
import middleware.constants as cons
from middleware.channels import InterProcess, TopicInterNode, Poller

class Detector(Process):

    def __init__(self, country, nodeid, config):

        self.aid = nodeid
        self.country = country
        self.config = config
        self.quit = False

        super(Detector, self).__init__()

    def _sig_handler(self, signum, frame):
        self.quit = True

    def _initialize(self):

        self.monitor = InterProcess(cons.PULL)
        self.monitor.connect("monitor-{}-{}".format(
                        self.country, self.aid))

        self.fail = InterProcess(cons.PUSH)
        self.fail.connect("fail-{}-{}".format(
                        self.country, self.aid))
        
        self.next = TopicInterNode([""])

        self.poller = Poller([self.next, self.monitor])

    def _monitor_node(self, first_time):

        # Receives id of the node
        # to be monitored
        mtype, nid = self.monitor.recv()
        print("country: {}, node: {} - recv (mtype: {}, nid: {})".format(
                self.country, self.aid, mtype, nid))

        # If the message type is "CLEAR"
        # it means the node is the 'Leader'
        # and it does not need to monitor any node
        while mtype == m.CLEAR_MONITOR:
            mtype, nid = self.monitor.recv()
            print("country: {}, node: {} - recv (mtype: {}, nid: {})".format(
                    self.country, self.aid, mtype, nid))

        if not first_time:
            self.next.disconnect(self.config["retransmitter_endpoints"][self.country][int(self.monitor_node)]["alive"]["connect"])
        
        self.monitor_node = nid
        self.next.connect(self.config["retransmitter_endpoints"][self.country][int(nid)]["alive"]["connect"])

    def _start_monitor(self):

        self._monitor_node(True)

    def run(self):

        signal.signal(signal.SIGINT, self._sig_handler)

        # Initialize detector's connections
        self._initialize()

        print("Failure detector running. Country: {}, id: {}".format(
                    self.country, self.aid))

        self._start_monitor()
        
        while not self.quit:

            socks = self.poller.poll(cons.TIMEOUT)

            # Timeout passed
            if len(socks) == 0:
                self.fail.send({"mtype": m.FAIL, "node": self.monitor_node})
                self._monitor_node(False)

            for s, poll_type in socks:

                msg, nid = s.recv()
                
                if msg == m.START_MONITOR:
                    print("failure detector - country: {}, node: {} - recv START_MONITOR from: {}".format(
                            self.country, self.aid, nid))
                    interface = self.config["retransmitter_endpoints"][self.country][int(self.monitor_node)]["alive"]["connect"]
                    self.next.disconnect(interface)
                    self.monitor_node = nid
                    self.next.connect(interface)

                if msg == m.I_AM_ALIVE:
                    print("failure detector - country: {}, node: {} - recv I_AM_ALIVE from: {}".format(
                            self.country, self.aid, nid))

        self.fail.close()
        self.next.close()
        self.monitor.close()

        print("Failure detector from {} and id:{} down".format(
                self.country, self.aid))


