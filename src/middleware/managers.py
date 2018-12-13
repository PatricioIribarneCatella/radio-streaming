import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import constants as cons
from channels import InterNode, InterProcess, Poller

class Leader(object):

    def __init__(self, country, nodes, aid, config):
        
        self.country = country
        self.nodes = nodes
        self.config = config
        self.aid = aid

        self.fd = InterProcess("{}/{}".format(country, aid), "bind")
        
        le = InterNode()
        le.bind(config["anthena"][country]["bind"], self.aid)

        self.sender = InterNode()
        self.poller = Poller([fd, le])

    def monitor(self, message):

        self.fd.send(message)

    def send(self, message, receivers):

        for rid in receivers:
            self.sender.connect(self.config["anthena"][self.country]["connect"], rid)
            self.sender.send(message)

    def recv(self):

        socks = self.poller.poll()

        for s, poll_type in socks:
            if poll_type == cons.POLLIN:
                msg, nid = s.recv()
                print("msg: {}, nid: {}".format(msg, nid))
                yield msg, nid



