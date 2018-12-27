import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import middleware.constants as cons
import rebroadcast.messages as m
from middleware.channels import InterNode, Poller

def search_leader(country, config):

    nodes = len(config["retransmitter_endpoints"][country])

    leader_found = False
    leader = None

    while not leader_found:
        
        antennas = [InterNode(cons.REQ)
                        for i in range(0, nodes)]

        for i in range(0, nodes):
            antennas[i].connect(config["retransmitter_endpoints"][country][i]["query-leader"]["connect"])
            antennas[i].set(cons.LINGER, 0)

        poller = Poller(antennas)

        for a in antennas:
            a.send({"mtype": m.IS_LEADER, "node": 0})

        i = len(antennas)

        answers = []
        
        while i > 0:
            
            socks = poller.poll(cons.TIMEOUT)

            if len(socks) == 0:
                i -= 1
        
            for s, poll_type in socks:
                answers.append(s.recv())
                i -= 1

        leader = list(filter(lambda x: x[0] == m.LEADER, answers))
        
        if len(leader) > 0:
            leader_found = True

        for a in antennas:
            a.close()

    return leader[0][1]


