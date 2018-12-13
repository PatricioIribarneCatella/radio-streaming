import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import middleware.constants as cons
from middleware.channels import InterNode, InterProcess, Poller

class Leader(object):

    def __init__(self, country, nodes, aid, config):
        
        self.country = country
        self.nodes = nodes
        self.config = config
        self.aid = aid

        self.anthena = InterNode(cons.PUSH)

        self.monitor = InterProcess(cons.PUSH)
        self.monitor.bind("monitor/{}-{}".format(country, aid))
        
        fd = InterProcess(cons.PULL)
        fd.bind("fail/{}-{}".format(country, aid))
        
        le = InterNode(cons.PULL)
        le.bind(config["anthena"][country][self.aid]["bind"])

        self.poller = Poller([fd, le])

    def monitor(self, message):

        self.monitor.send(message)

    def send(self, message, receivers):

        for rid in receivers:
            interface = self.config["anthena"][self.country][rid]["connect"]
            self.anthena.connect(interface)
            self.anthena.send(message)

    def recv(self):

        socks = self.poller.poll()

        for s, poll_type in socks:
            if poll_type == cons.POLLIN:
                msg, nid = s.recv()
                print("msg: {}, nid: {}".format(msg, nid))
                yield msg, nid



