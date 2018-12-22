import re
import zmq 
import random
from multiprocessing import Process

from audio.player import AudioPlayer

class InvalidFrequency(Exception):
    pass

class Receiver(Process):

    def __init__(self, country, frequency_code, config):
        
        match = re.match(r'^(\w{2,3})-\d{2,3}\.\d$', frequency_code)
        
        if match is None:
            raise InvalidFrequency

        self.freq_country = match.group(1)
        self.connection_country = country
        self.admin_endpoint = None
        self.frequency_code = frequency_code
        
        if self.connection_country != self.freq_country:
            self.admin_endpoint = random.choice(config['retransmitter_endpoints'][self.connection_country])['admin']
        
        self.broadcasters_endpoints = map(lambda x: x['output'], config['retransmitter_endpoints'][self.connection_country])
        self.player = AudioPlayer(config.get('bitrate', 16000))


    def _start_connections(self):
        
        self.context = zmq.Context()
        self.broadcasters_sockets = []
        self.poller = zmq.Poller()

        for broadcasters_endpoint in self.broadcasters_endpoints:
            new_broadcast_socket = self.context.socket(zmq.SUB)
            new_broadcast_socket.connect('tcp://{}'.format(broadcasters_endpoint))
            self.poller.register(new_broadcast_socket, zmq.POLLIN)
            self.broadcasters_sockets.append(new_broadcast_socket)
            new_broadcast_socket.setsockopt_string(zmq.SUBSCRIBE, self.frequency_code)
        
        self.admin_socket = None
        
        if self.admin_endpoint:
            self.admin_socket = self.context.socket(zmq.REQ)
            self.admin_socket.connect('tcp://{}'.format(self.admin_endpoint))
            self.admin_socket.send_json({'type': 'listen_other_country', 'frequency': self.frequency_code})
            return self.admin_socket.recv_json()['status'] == 'ok'
        
        return True

    def _get_chunks(self):
        
        for socket_with_data in dict(self.poller.poll(100)):
            topic, message = socket_with_data.recv_multipart()
            yield topic, message

    def _close(self):
        
        if self.admin_socket:
            self.admin_socket.send_json({'type': 'stop_listen_other_country', 'frequency': self.frequency_code})
            self.admin_socket.recv_json()
            self.admin_socket.close()
        
        for broadcaster_socket in self.broadcasters_sockets:
            broadcaster_socket.close()
        
        self.context.term()
        self.player.close()

    def run(self):
        
        listening = self._start_connections()
        
        try:
            if listening:
                while True:
                    for _, chunk in self._get_chunks():
                        self.player.play(chunk)
        except KeyboardInterrupt:
            pass
        
        self._close()
    

