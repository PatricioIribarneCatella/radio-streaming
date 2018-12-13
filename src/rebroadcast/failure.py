import sys
import time
from os import path
from multiprocessing import Process

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from middleware.channels import InterProcess, InterNode
import middleware.constants as cons
import messages as m

class Detector(Process):

    def __init__(self, country, nodeid, config):

        self.nodeid = nodeid
        self.country = country
        self.config = config

        self.node = InterProcess("{}/{}".format(
                        country, nodeid), "connect")
        
        self.next = InterNode()

        super(Detector, self).__init__()

    def _monitor_node(self):
        
        # Receives id of the node
        # to be monitored
        mtype, nid = self.node.recv()

        # If the message type is "CLEAR"
        # it means the node is the 'Leader'
        # and it does not need to monitor any node
        while mtype == m.CLEAR_MONITOR:
            mtype, nid = self.node.recv()

        self.next.connect(config["anthena"][self.country]["connect"],
                          int(nid), timeout=1)

    def run(self):

        self._monitor_node()
        
        while True:

            self.next.send({"mtype": m.IS_ALIVE,
                            "from": self.nodeid})

            msg, error = self.next.recv()

            if error != None:
                if error == cons.TIMEOUT:
                    self.node.send({"mtype": m.FAIL})
                    self._monitor_node()
                else:
                    print("An error ocurred: {}".format(error))
            
            # Simulate time passed
            time.sleep(1)

        self.node.close()
        self.next.close()

        print("Failure detector from {} and id:{} down".format(
                self.country, self.nodeid))


