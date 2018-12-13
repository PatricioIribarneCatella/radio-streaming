class NodeState(object):

    def leader(self):
        return self.state

class Leader(NodeState):

    def __init__(self):
        self.state = True

class Normal(NodeState):

    def __init__(self):
        self.state = False



