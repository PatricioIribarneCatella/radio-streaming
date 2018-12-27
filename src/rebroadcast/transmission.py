import re
import sys
import zmq
import random
from os import path
from time import sleep
from multiprocessing import Process

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import rebroadcast.messages as m
from rebroadcast.transmiting_state import TransmitingState, InUseFreq
from rebroadcast.listening_state import ListeningState

class Retransmitter(Process):

    def __init__(self, country, node_number, config):
        
        self.country = country
        self.node_number = node_number
        
        self.input_endpoint = config['retransmitter_endpoints'][country][node_number]['input']
        self.output_endpoint = config['retransmitter_endpoints'][country][node_number]['output']
        self.admin_endpoint = config['retransmitter_endpoints'][country][node_number]['admin']
        
        self.routers_endpoints = list(map(lambda x: x['output'], config['routers_endpoints']))
        self.outgoing_router = random.choice(config['routers_endpoints'])['input']
        
        self.transmitting_state = TransmitingState()
        self.listening_state = ListeningState()
        
        super(Retransmitter, self).__init__()

    def _start_connections(self):
        
        self.context = zmq.Context()
        self.poller = zmq.Poller()

        self.input_socket = self.context.socket(zmq.PULL)
        self.input_socket.bind('tcp://{}'.format(self.input_endpoint))
        self.poller.register(self.input_socket, zmq.POLLIN)

        self.router_sockets = []
        for router_endpoint in self.routers_endpoints:
            router_socket = self.context.socket(zmq.SUB)
            router_socket.connect('tcp://{}'.format(router_endpoint))
            self.poller.register(router_socket, zmq.POLLIN)
            self.router_sockets.append(router_socket)

        self.output_socket = self.context.socket(zmq.PUB)
        self.output_socket.bind('tcp://{}'.format(self.output_endpoint))

        self.outgoing_router_socket = self.context.socket(zmq.PUSH)
        self.outgoing_router_socket.connect('tcp://{}'.format(self.outgoing_router))

        self.admin_socket = self.context.socket(zmq.REP)
        self.admin_socket.bind('tcp://{}'.format(self.admin_endpoint))
        self.poller.register(self.admin_socket, zmq.POLLIN)

    def _transmit_message(self, frequency, message):

        self.transmitting_state.update(frequency.decode())

        self.output_socket.send_multipart([frequency, message])
        
        print('sending {} {}'.format(frequency, self.outgoing_router))
        
        if frequency.decode().startswith(self.country + '-'):
            self.outgoing_router_socket.send_multipart([frequency, message])
        
        print('sent {} {}'.format(frequency, self.outgoing_router))

    def _start_listening(self, frequency):

        print('Listening on {}'.format(frequency))
        
        for router_socket in self.router_sockets:
            router_socket.setsockopt_string(zmq.SUBSCRIBE, frequency)
    
    def _stop_listening(self, frequency):
        
        print('Stopping Listening on {}'.format(frequency))
        
        for router_socket in self.router_sockets:
            router_socket.setsockopt_string(zmq.UNSUBSCRIBE, frequency)

    def _treat_query(self, query):
       
        freq_code = query['frequency']
        match = re.match(r'^(\w{2,3})-\d{2,3}\.\d$', freq_code)
        
        if match is None:
            return {"mtype": m.INVALID_FREQ,
                    "node": self.node_number}

        country = match.group(1)

        if query['type'] == m.START_TRANSMITTING:
            
            if country != self.country:
                return {"mtype": m.NOT_SAME_COUNTRY,
                        "node": self.node_number}
            try:
                self.transmitting_state.add(query['frequency'])
            except InUseFreq:
                return {"mtype": m.IN_USE_FREQ,
                        "node": self.node_number}

        elif query['type'] == m.LISTEN_OTHER_COUNTRY:
            
            if country == self.country:
                return {"mtype": m.SAME_COUNTRY,
                        "node": self.node_number}

            should_start_listening = self.listening_state.add(freq_code)
            
            if should_start_listening:
                self._start_listening(freq_code)
        
        elif query['type'] == m.STOP_LISTEN_OTHER_COUNTRY:
            
            if country == self.country:
                return {"mtype": m.SAME_COUNTRY,
                        "node": self.node_number}

            should_stop_listening = self.listening_state.remove(freq_code)
            
            if should_stop_listening:
                self._stop_listening(freq_code)
        else:
            return {"mtype": m.NOT_IMPLEMENTED_QUERY,
                    "node": self.node_number}
        
        return {'mtype': m.OK, 'node': self.node_number}

    def _respond_admin_queries(self):
       
        query = self.admin_socket.recv_json()
        response = self._treat_query(query)
        self.admin_socket.send_json(response)

    def _retransmit(self):
        
        while True:
            for socket_with_data, _ in self.poller.poll(100):
                if socket_with_data is self.admin_socket:
                    self._respond_admin_queries()
                else:
                    freq, data = socket_with_data.recv_multipart()
                    self._transmit_message(freq, data)

    def _close(self):
        
        self.output_socket.close()
        self.input_socket.close()
        self.context.term()

    def run(self):
        
        print("Transmitter module running - country: {} id: {}".format(
            self.country, self.node_number))
        
        self._start_connections()
        self._retransmit()
        self._close()

