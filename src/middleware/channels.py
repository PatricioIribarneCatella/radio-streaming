import zmq

IPC_SOCK_DIR = "/tmp/"
TCP_CONN = "tcp://"
IPC_CONN = "ipc://"

class TimeOut(Exception):
    pass

class InterProcess(object):

    def __init__(self, sock_type):
        self.socket = zmq.Context().socket(sock_type)

    def bind(self, interface):
        self.socket.bind(IPC_CONN + IPC_SOCK_DIR + interface)

    def connect(self, interface):
        self.socket.connect(IPC_CONN + IPC_SOCK_DIR + interface)

    def get_connection(self):
        return self.socket

    def send(self, message):
        self.socket.send_json(message)

    def recv(self):
        data = self.socket.recv_json()
        return data["mtype"], data["node"]

    def close(self):
        self.socket.close()

class InterNode(object):

    def __init__(self, sock_type):

        self.socket = zmq.Context().socket(sock_type)

    def bind(self, interface):
        self.socket.bind("{}{}:{}".format(
                                TCP_CONN,
                                interface["ip"],
                                interface["port"]))

    def connect(self, interface, timeout=0):
    
        if timeout > 0:
            self.socket.setsockopt(zmq.RCVTIMEO, timeout*1000)

        self.socket.connect("{}{}:{}".format(
                                TCP_CONN,
                                interface["ip"],
                                interface["port"]))

    def disconnect(self, interface):

        if interface != None:
            self.socket.disconnect("{}{}:{}".format(
                                    TCP_CONN,
                                    interface["ip"],
                                    interface["port"]))

    def get_connection(self):
        return self.socket

    def send(self, message):
        self.socket.send_json(message)

    def recv(self):
        
        try:
            data = self.socket.recv_json()
        except zmq.Again:
            raise TimeOut()
        
        return data["mtype"], data["node"]

    def close(self):
        self.socket.close()

class TopicInterNode(InterNode):

    def __init__(self, topics):
        super(TopicInterNode, self).__init__(zmq.SUB)
        for topic in topics:
            self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)

class PublishInterNode(InterNode):

    def __init__(self):
        super(PublishInterNode, self).__init__(zmq.PUB)

class Channel(object):

    def __init__(self, socket):

        self.s = socket
    
    def recv(self):

        data = self.s.recv_json()
        return data["mtype"], data["node"]

    def send(self, message):

        self.s.send_json(message)

class Poller(object):

    def __init__(self, socks):

        self.poller = zmq.Poller()

        self.socks = socks

        for s in socks:
            self.poller.register(s.get_connection(), zmq.POLLIN)

    def poll(self, timeout=None):

        if timeout != None:
            timeout *= 1000

        sockets = self.poller.poll(timeout)

        return list(map(lambda t: (Channel(t[0]), t[1]), sockets))

    def close(self):
        for s in self.socks:
            s.close()



