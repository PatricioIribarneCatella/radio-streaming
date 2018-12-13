import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from middleware.managers import Leader
from failure import Detector
import messages as m

class Anthena(object):

    def __init__(self, country, nodes, aid, config):

        self.country = country
        self.nodes = nodes
        self.config = config
        self.aid = aid
        
        self.connection = Leader(self.country, self.nodes, self.aid)

        self.handlers = {
            m.ALIVE: self._react_on_alive,
            m.FAIL: self._react_on_fail,
            m.IS_LEADER: self._react_on_leader_question,
            m.IS_ALIVE: self._react_on_alive_question
        }

    def _lesser(self):

        return [i for i in range(1, self.aid)]

    def _react_on_alive(self, nid):

        if (self.next > nid) or (self.next == None):
            
            self.connection.monitor({"mtype": m.START_MONITOR, "node": nid})
            
            if self.next == None:
                self.state = Normal()

            self.next = nid

    def _react_on_fail(self, nid):

        nid += 1

        if nid > self.nodes:
            self.state = Leader()
            self.connection.monitor({"mtype": m.CLEAR_MONITOR, "node": 0})
            self.next = None
        else:
            self.connection.monitor({"mtype": m.START_MONITOR, "node": nid})
            self.next = nid

    def _react_on_leader_question(self, nid):

        mtype = m.LEADER if self.state.leader() else m.NOT_LEADER

        self.connection.send({"mtype": mtype, "node": self.aid}, [nid])

    def _react_on_alive_question(self, nid):

        self.connection.send({"mtype": m.REPLY_ALIVE, "node": self.aid},
                                [nid])

    def _recovery(self):

        # Notifies nodes with smaller priority that its alive
        self.connection.send({"mtype": m.ALIVE, "node": self.aid},
                                self._lesser())

        nextid = self.aid + 1

        if nextid > self.nodes:
            # This node is the leader
            self.state = Leader()
            self.connection.monitor({"mtype": m.CLEAR_MONITOR, "node": 0})
            self.next = None
        else:
            # Starts monitoring the next node
            self.connection.monitor({"mtype": m.START_MONITOR, "node": nextid})
            self.next = nextid
            self.state = Normal()

    def _loop(self):

        for msg, nid in self.connection.recv():

            handler = self.handlers.get(msg)

            handler(nid)

    def run(self):

        print("Anthena running")

        d = Detector(self.country, self.aid, self.config)
        d.start()

        self._recovery()

        try:
            while True:
                self._loop()
        except KeyboardInterrupt:
            d.join()

        print("Leader module down")


