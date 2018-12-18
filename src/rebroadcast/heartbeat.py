import sys
import time
from os import path
from multiprocessing import Process

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import rebroadcast.messages as m
import middleware.constants as cons
from middleware.channels import PublishInterNode

class HeartbeatSender(Process):

    def __init__(self, country, nodeid, config):

        self.aid = nodeid
        self.country = country
        self.config = config

        super(HeartbeatSender, self).__init__()

    def _initialize(self):

        self.heartbeat = PublishInterNode()
        self.heartbeat.bind(self.config["anthena"][self.country][str(self.aid)]["alive"]["bind"])

    def run(self):

        self._initialize()

        while True:

            self.heartbeat.send({"mtype": m.I_AM_ALIVE, "node": self.aid})

            time.sleep(cons.HB_TIME)

        self.heartbeat.close()


