import sys
import time
from os import path
from threading import Thread, Event
import zmq
from datetime import datetime

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import rebroadcast.messages as m
import middleware.constants as cons
from middleware.channels import PublishInterNode

class HeartbeatListener(Thread):
    def __init__(self, endpoints, feedback_timestamps):
        self.endpoints = endpoints
        self.feedback_timestamps = feedback_timestamps
        self.quit = Event()
        super(HeartbeatListener, self).__init__()

    def shutdown(self):
        self.quit.set()

    def _start_connections(self):
        self.context = zmq.Context()
        self.poller = zmq.Poller()
        self.heartbeat_sockets = []
        for heartbeat_endpoint in self.endpoints:
            heartbeat_socket = self.context.socket(zmq.SUB)
            heartbeat_socket.connect('tcp://{}:{}'.format(heartbeat_endpoint['ip'], heartbeat_endpoint['port']))
            heartbeat_socket.setsockopt_string(zmq.SUBSCRIBE, "")
            self.heartbeat_sockets.append(heartbeat_socket)
            self.poller.register(heartbeat_socket, zmq.POLLIN)

    
    def run(self):
        self._start_connections()
        while not self.quit.is_set():
            for socket_with_data, _ in self.poller.poll():
                message = socket_with_data.recv_json()
                if message['mtype'] == m.I_AM_ALIVE:
                    self.feedback_timestamps[message['node']] = datetime.now()

    def _close(self):
        self.context.close()
