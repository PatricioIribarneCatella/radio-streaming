import zmq 
from multiprocessing import Process
from audio.player import AudioPlayer
import re


class InvalidFrequency(Exception):
    pass

class Receiver(Process):

    def __init__(self, frequency_code, config):
        match = re.match(r'^(\w{2,3})-\d{2,3}\.\d$', frequency_code)
        if match is None:
            raise InvalidFrequency

        self.country = match.group(1)
        self.broadcasters_endpoints = map(lambda x: x['output'], config['retransmitter_endpoints'][self.country])

        self.frequency_code = frequency_code
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

    def _get_chunks(self):
        for socket_with_data in dict(self.poller.poll(100)):
            topic, message = socket_with_data.recv_multipart()
            yield topic, message

    def run(self):
        self._start_connections()
        while True:
            for _, chunk in self._get_chunks():
                self.player.play(chunk)
        self._close()
    
    def _close(self):
        for socket in self.broadcasters_endpoints:
            self.broadcasters_endpoints.close()
        self.context.term()
        self.player.close()