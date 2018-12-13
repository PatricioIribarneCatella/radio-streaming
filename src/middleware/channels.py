import zmq

class InterProcess(object):

    def __init__(self, sock_type):
        self.socket = zmq.Context().socket(sock_type)

    def bind(self, interface):
        self.socket.bind(interface)

    def connect(self, interface):
        self.socket.connect(interface)

    def get_connection(self):
        return self.socket

    def send(self, message):

    def recv(self):

    def close(self):
        self.socket.close()

class InterNode(object):

    def __init__(self, sock_type):
        self.socket = zmq.Context().socket(sock_type)

    def bind(self, interface):
        self.socket.bind("tcp:{}:{}".format(interface["ip"],
                                interface["port"]))

    def connect(self, interface):
        self.socket.bind("tcp:{}:{}".format(interface["ip"],
                                interface["port"]))

    def get_connection(self):
        return self.socket

    def send(self, message):

    def recv(self):

    def close(self):
        self.socket.close()

class Poller(object):

    def __init__(self, socks):

        self.poller = zmq.Poller()

        self.socks = socks

        for s in socks:
            self.poller.register(s.get_connection(), zmq.POLLIN)

    def poll(self):

        return dict(self.poller.poll())

    def close(self):
        for s in self.socks:
            s.close()



