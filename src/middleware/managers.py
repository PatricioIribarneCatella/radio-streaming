import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import middleware.constants as cons
import rebroadcast.messages as m
from stations.utils import search_leader
from middleware.channels import InterNode, DataTopicInterNode, InterProcess, DataInterProcess, Poller

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

        self.transmitter = DataInterProcess(cons.PUSH)
        self.transmitter.bind("station-sender-data-{}".format(
                            self.frequency))
        
    def query(self):

        lid = search_leader(self.country, self.config)

        # Connects to leader
        # and sends a 'transmitting request'
        admin = InterNode(cons.REQ)
        admin.connect(self.config["retransmitter_endpoints"][self.country][lid]["admin"])

        admin.send({"type": m.START_TRANSMITTING,
                    "frequency": self.frequency})

        mtype, node = admin.recv()

        admin.close()

        return mtype == m.OK

    def transmit(self, chunk):

        data = {"mtype": m.NEW_DATA,
                "freq":self.frequency,
                "data": chunk}

        self.transmitter.send(data)

    def close(self):

        self.transmitter.close()


class ReceiverStation(object):

    def __init__(self, freq, country, config):
 
        self.country = country
        self.freq = freq
        self.config = config

        broadcasters = map(lambda x: x['output'], config['retransmitter_endpoints'][self.country])

        self.receivers = []

        for endpoint in broadcasters:
            s = DataTopicInterNode([self.freq])
            s.connect(endpoint)
            self.receivers.append(s)

        self.poller = Poller(self.receivers)

    def recv(self):

        socks = self.poller.poll(0.1)

        for s, poll_type in socks:
            if poll_type == cons.POLLIN:
                freq, data = s.recv()
                yield data

    def close(self):

        for s in self.receivers:
            s.close()

class InternationalReceiverStation(object):

    def __init__(self):
        pass

    def run(self):
        pass


