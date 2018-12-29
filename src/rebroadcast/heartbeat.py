import sys
import time
import signal
from os import path
from multiprocessing import Process

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import rebroadcast.messages as m
import middleware.constants as cons
from middleware.channels import PublishInterNode, InterProcess

class HeartbeatSender(Process):

    def __init__(self, country, nodeid, config):

        self.aid = nodeid
        self.country = country
        self.config = config
        self.quit = False

        super(HeartbeatSender, self).__init__()

    def _sig_handler(self, signum, frame):
        self.quit = True

    def _initialize(self):

        self.leader = InterProcess(cons.PULL)
        self.leader.connect("heartbeat-{}-{}".format(self.country, self.aid))

        self.heartbeat = PublishInterNode()
        self.heartbeat.bind(self.config["retransmitter_endpoints"][self.country][int(self.aid)]["alive"]["bind"])

    def run(self):

        signal.signal(signal.SIGINT, self._sig_handler)

        self._initialize()

        is_leader, nid = self.leader.recv()

        while not self.quit:

            self.heartbeat.send({"mtype": m.I_AM_ALIVE,
                                 "node": {
                                     "id": self.aid,
                                     "state": is_leader
                                 }})

            e = self.leader.poll(cons.HB_TIME)

            # Leader coordinator sent a notification
            # because state changed
            if e != cons.NO_EVENTS:
                is_leader, nid = self.leader.recv()
            else:
                time.sleep(cons.HB_TIME)

        self.heartbeat.close()
        self.leader.close()


