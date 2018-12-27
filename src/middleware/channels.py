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

    def get_recv_format(self):
        return "json"

    def get_connection(self):
        return self.socket

    def poll(self, timeout):
        return self.socket.poll(timeout)

    def send(self, message):
        self.socket.send_json(message)

    def recv(self):
        data = self.socket.recv_json()
        return tuple(data.values())

    def close(self):
        self.socket.close()

class InterNode(object):

    def __init__(self, sock_type):

        self.socket = zmq.Context().socket(sock_type)

    def set(self, opt, value):

        self.socket.setsockopt(opt, value)

    def bind(self, interface):

        if type(interface) == str:
            self.socket.bind("{}{}".format(
                                TCP_CONN,
                                interface))
        else:
            self.socket.bind("{}{}:{}".format(
                                TCP_CONN,
                                interface["ip"],
                                interface["port"]))

    def connect(self, interface, timeout=0):
    
        if timeout > 0:
            self.socket.setsockopt(zmq.RCVTIMEO, timeout*1000)

        if type(interface) == str:
            self.socket.connect("{}{}".format(
                                TCP_CONN,
                                interface))
        else:
            self.socket.connect("{}{}:{}".format(
                                TCP_CONN,
                                interface["ip"],
                                interface["port"]))

    def disconnect(self, interface):

        if interface != None:
            if type(interface) == str:
                self.socket.disconnect("{}{}".format(
                                        TCP_CONN,
                                        interface))
            else:
                self.socket.disconnect("{}{}:{}".format(
                                        TCP_CONN,
                                        interface["ip"],
                                        interface["port"]))

    def get_connection(self):
        return self.socket

    def get_recv_format(self):
        return "json"

    def send(self, message):
        self.socket.send_json(message)

    def recv(self):
        
        try:
            data = self.socket.recv_json()
        except zmq.Again:
            raise TimeOut()
        
        return tuple(data.values())

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

class DataInterProcess(InterProcess):

    def __init__(self, sock_type):
        super(DataInterProcess, self).__init__(sock_type)

    def get_recv_format(self):
        return "multipart"

    def send(self, data):

        msg = [str(data["mtype"]).encode(),
                data["freq"].encode(),
                data["data"]]

        self.socket.send_multipart(msg)

    def recv(self):

        mtype, freq, data = self.socket.recv_multipart()

        return int(mtype.decode()), {"freq": freq.decode(), "data": data}

class DataInterNode(InterNode):

    def __init__(self, sock_type):
        super(DataInterNode, self).__init__(sock_type)

    def get_recv_format(self):
        return "multipart"

    def send(self, data):

        msg = [data["freq"].encode(), data["data"]]

        self.socket.send_multipart(msg)

    def recv(self):

        freq, data = self.socket.recv_multipart()

        return freq.decode(), data

class DataTopicInterNode(DataInterNode):

    def __init__(self, topics):
        super(DataTopicInterNode, self).__init__(zmq.SUB)
        for topic in topics:
            self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)

    def get_recv_format(self):
        return "multipart-topic"

class Channel(object):

    def __init__(self, socket, recv_type):

        self.s = socket
        self.recv_type = recv_type
    
    def recv(self):

        if self.recv_type == "json":
            data = self.s.recv_json()
            return tuple(data.values())
        elif self.recv_type == "multipart":
            mtype, freq, data = self.s.recv_multipart()
            return int(mtype.decode()), {"freq": freq.decode(), "data": data}
        elif self.recv_type == "multipart-topic":
            freq, data = self.s.recv_multipart()
            return freq.decode(), data

    def send(self, message):

        self.s.send_json(message)

class Poller(object):

    def __init__(self, socks):

        self.poller = zmq.Poller()

        self.socks = socks

        self.socks_types = dict([(s.get_connection(), s.get_recv_format())
                                    for s in self.socks])

        for s in socks:
            self.poller.register(s.get_connection(), zmq.POLLIN)

    def poll(self, timeout):

        if timeout != None:
            timeout *= 1000

        sockets = self.poller.poll(timeout)

        return list(map(lambda t: (Channel(t[0], self.socks_types[t[0]]), t[1]), sockets))

    def close(self):
        for s in self.socks:
            s.close()



