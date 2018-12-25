import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import middleware.constants as cons
import rebroadcast.messages as m
from middleware.channels import InterNode, Poller

def search_leader(country, config):

    nodes = len(config["retransmitter_endpoints"][country])

    antennas = [InterNode(cons.REQ)
                    for i in range(0, nodes)]

    for i in range(0, nodes):
        antennas[i].connect(config["retransmitter_endpoints"][country][i]["query-leader"]["connect"])
        antennas[i].set(cons.LINGER, 0)

    poller = Poller(antennas)

    leader_found = False
    leader = None

    while not leader_found:

        for a in antennas:
            a.send({"mtype": m.IS_LEADER, "node": 0})

        socks = poller.poll()

        answers = []
        
        for s, poll_type in socks:
            answers.append(s.recv())

        leader = list(filter(lambda x: x["mtype"] == m.LEADER, answers))
        
        if len(leader) > 0:
            leader_found = True

    return leader[0]


