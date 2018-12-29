import sys
import zmq
import time
from os import path
from datetime import datetime
from threading import Thread, Event

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import rebroadcast.messages as m
import middleware.constants as cons
from middleware.channels import TopicInterNode, Poller

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
        heartbeat_sockets = []
        
        for heartbeat_endpoint in self.endpoints:
            heartbeat_socket = TopicInterNode([""])
            heartbeat_socket.connect(heartbeat_endpoint)
            heartbeat_sockets.append(heartbeat_socket)
        
        self.poller = Poller(heartbeat_sockets)
    
    def run(self):
        
        self._start_connections()
        
        while not self.quit.is_set():
        
            for socket, _ in self.poller.poll():
                message_type, node_number = socket.recv()

                if message_type == m.I_AM_ALIVE:
                    self.feedback_timestamps[node_number] = datetime.now()

    def _close(self):
        self.context.close()

