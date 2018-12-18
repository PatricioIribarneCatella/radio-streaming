import sys
import time
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

        super(Detector, self).__init__()

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
        print("node: {} recv mtype: {}, nid: {}".format(self.aid, mtype, nid))

        # If the message type is "CLEAR"
        # it means the node is the 'Leader'
        # and it does not need to monitor any node
        while mtype == m.CLEAR_MONITOR:
            mtype, nid = self.monitor.recv()
            print("node: {}, mtype: {}, nid: {}".format(self.aid, mtype, nid))
        
        print("hola")
        
        if not first_time:
            self.next.disconnect(self.config["anthena"][self.country][str(self.monitor_node)]["alive"]["connect"])
        
        self.monitor_node = nid
        self.next.connect(self.config["anthena"][self.country][str(nid)]["alive"]["connect"])
        
        print("hola2")

    def _start_monitor(self):

        self._monitor_node(True)

    def run(self):

        # Initialize detector´s connections
        self._initialize()

        print("Failure detector running. Country: {}, id: {}".format(
                    self.country, self.aid))

        self._start_monitor()
        
        while True:

            socks = self.poller.poll(cons.TIMEOUT)

            # Timeout passed
            if len(socks) == 0:
                self.fail.send({"mtype": m.FAIL, "node": self.monitor_node})
                self._monitor_node(False)

            for s, poll_type in socks:

                msg, nid = s.recv()
                
                if msg == m.START_MONITOR:
                    print("failure detector node: {} - recv START_MONITOR from: {}".format(self.aid, nid))
                    self.next.disconnect(self.config["anthena"][self.country][str(self.monitor_node)]["alive"]["connect"])
                    self.monitor_node = nid
                    self.next.connect(self.config["anthena"][self.country][str(self.monitor_node)]["alive"]["connect"])

                if msg == m.I_AM_ALIVE:
                    print("failure detector node: {} - recv I_AM_ALIVE from: {}".format(self.aid, nid))

            print("hola3")

        self.node.close()
        self.next.close()

        print("Failure detector from {} and id:{} down".format(
                self.country, self.aid))


