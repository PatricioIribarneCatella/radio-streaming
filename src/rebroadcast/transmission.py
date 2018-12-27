import re
import sys
import zmq
import random

from os import path
from time import sleep
from datetime import datetime, timedelta
from random import shuffle, randint
from multiprocessing import Process

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import rebroadcast.messages as m
from middleware import constants as c
from rebroadcast.transmiting_state import TransmitingState, InUseFreq
from rebroadcast.listening_state import ListeningState
from rebroadcast.heartbeat_router_listener import HeartbeatListener

class Retransmitter(Process):

    def __init__(self, country, node_number, config):
        
        self.country = country
        self.node_number = node_number
        
        self.input_endpoint = config['retransmitter_endpoints'][country][node_number]['input']
        self.output_endpoint = config['retransmitter_endpoints'][country][node_number]['output']
        self.admin_endpoint = config['retransmitter_endpoints'][country][node_number]['admin']
        
        self.routers_endpoints = list(map(lambda x: x['output'], config['routers_endpoints']))
        
        self.possible_outgoing_routers_heartbeat = \
                list(map(lambda x: x['heartbeat']['connect'], config['routers_endpoints']))
        
        self.current_outgoing_router = random.randint(0, len(self.possible_outgoing_routers_heartbeat) - 1)
        
        print('Picked router {}'.format(self.current_outgoing_router))
        
        self.possible_outgoing_routers_endpoint = map(lambda x: x['input'], config['routers_endpoints'])
        self.router_last_timestamp_alive = [datetime.now() for i in self.possible_outgoing_routers_heartbeat]
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

        self.outgoing_router_socket = []
        
        for router_endpoint in self.possible_outgoing_routers_endpoint:
            outgoing_router_socket = self.context.socket(zmq.PUSH)
            outgoing_router_socket.connect('tcp://{}'.format(router_endpoint))
            self.outgoing_router_socket.append(outgoing_router_socket)

        self.monitor = HeartbeatListener(self.possible_outgoing_routers_heartbeat,
                                         self.router_last_timestamp_alive)
        self.monitor.start()

        self.admin_socket = self.context.socket(zmq.REP)
        self.admin_socket.bind('tcp://{}'.format(self.admin_endpoint))
        self.poller.register(self.admin_socket, zmq.POLLIN)

    def _get_outgoing_socket(self):
        
        now = datetime.now()
        
        if now - self.router_last_timestamp_alive[self.current_outgoing_router] < timedelta(seconds=c.TIMEOUT):
            return self.outgoing_router_socket[self.current_outgoing_router]
        
        self.current_outgoing_router = None

        while self.current_outgoing_router is None:
            
            now = datetime.now()
            outgoing_routers = list(enumerate(self.router_last_timestamp_alive))
            shuffle(outgoing_routers)
            
            print('changing router')
            
            for i, timestamp in outgoing_routers:
                if now - timestamp < timedelta(seconds=c.TIMEOUT):
                    self.current_outgoing_router = i
                    break
            
            if self.current_outgoing_router == None:
                sleep(c.ROUTER_RECONNECT_TRIAL)

        print('router selected {}'.format(self.current_outgoing_router))
        return self.outgoing_router_socket[self.current_outgoing_router]       

    def _transmit_message(self, frequency, message):
        
        self.transmitting_state.update(frequency.decode())
        
        outgoing_socket  = self._get_outgoing_socket()

        self.output_socket.send_multipart([frequency, message])
        
        print('sending {} to {} - from {}-{}'.format(frequency,
                self.output_endpoint, self.country, self.node_number))
        
        # Dont retransmit to router international freq
        if frequency.decode().startswith(self.country + '-'): 
            outgoing_socket.send_multipart([frequency, message])
            print('sent {} to {} - from {}-{}'.format(frequency,
                self.current_outgoing_router, self.country, self.node_number))

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

        self.monitor.shutdown()
        self.monitor.join()
        self.output_socket.close()
        self.input_socket.close()
        self.context.term()

    def run(self):
        
        print("Transmitter module running - country: {} id: {}".format(
            self.country, self.node_number))
        
        self._start_connections()
        self._retransmit()
        self._close()

