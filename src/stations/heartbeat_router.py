import sys
import time
from os import path
from threading import Thread, Event

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import rebroadcast.messages as m
import middleware.constants as cons
from middleware.channels import PublishInterNode

class HeartbeatSender(Thread):

    def __init__(self, nodeid, output_endpoint):

        self.nodeid = nodeid
        self.output_endpoint = output_endpoint
        self.quit = False
        self.shutdown_flag = Event()

        super(HeartbeatSender, self).__init__()

    
    def shutdown(self):
        self.shutdown_flag.set()

    def _initialize(self):
        print('connecting to {}'.format(self.output_endpoint))


        self.heartbeat = PublishInterNode()
        self.heartbeat.bind(self.output_endpoint)

    def run(self):
 

        self._initialize()

        while not self.shutdown_flag.is_set():
            print('Hello')

            self.heartbeat.send({"mtype": m.I_AM_ALIVE, "node": self.nodeid})

            time.sleep(cons.HB_TIME)

        self.heartbeat.close()
