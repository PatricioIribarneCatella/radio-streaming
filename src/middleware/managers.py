import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import middleware.constants as cons
import rebroadcast.messages as m
from stations.utils import search_leader
from middleware.channels import InterNode, InterProcess, Poller

class LeaderElection(object):

    def __init__(self, country, aid, config):
        
        self.country = country
        self.config = config
        self.aid = aid

        self.anthena = InterNode(cons.PUSH)

        self.monitorc = InterProcess(cons.PUSH)
        self.monitorc.bind("monitor-{}-{}".format(country, aid))

        self.lq = InterNode(cons.REP)
        self.lq.bind(config["retransmitter_endpoints"][country][int(self.aid)]["query-leader"]["bind"])

        fd = InterProcess(cons.PULL)
        fd.bind("fail-{}-{}".format(country, aid))
        
        le = InterNode(cons.PULL)
        le.bind(config["retransmitter_endpoints"][country][int(self.aid)]["bind"])

        self.poller = Poller([fd, le, self.lq])

    def monitor(self, message):

        self.monitorc.send(message)

    def send(self, message, receivers, node_type):

        interface = None
        
        if node_type == "station":
            self.lq.send(message)
        else:
            for rid in receivers:
                self.anthena.disconnect(interface)
                interface = self.config[node_type][self.country][int(rid)]["connect"]
                self.anthena.connect(interface)
                self.anthena.send(message)

    def recv(self):

        socks = self.poller.poll(None)

        for s, poll_type in socks:
            if poll_type == cons.POLLIN:
                msg, nid = s.recv()
                yield msg, nid

class SenderStation(object):

    def __init__(self, country, freq, config):
        
        self.country = country
        self.frequency = freq
        self.config = config

        self.transmitter = InterProcess(cons.PUSH)
        self.transmitter.bind("station-sender-data-{}".format(
                            self.frequency))
        
    def query(self):

        leader = search_leader(self.country, self.config)

        lid = int(leader["node"])

        # Connects to leader
        # and sends a 'transmitting request'

        admin = InterNode(cons.REQ)
        admin.connect(self.config["retransmitter_endpoints"][self.country][lid]["admin"])

        admin.send({"type": m.START_TRANSMITTING,
                    "frequency": self.frequency})

        res = admin.recv()

        return res["status"] == "ok"

    def transmit(self, chunk):

        data = {"mtype": m.NEW_DATA, "data": chunk}

        self.transmitter.send(data)

    def close(self):

        self.transmitter.close()


