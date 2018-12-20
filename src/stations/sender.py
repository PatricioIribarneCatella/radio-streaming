import re
import zmq
import random
from time import sleep
from scipy.io import wavfile
from multiprocessing import Process

class Sender(Process):

    def __init__(self, frequency_code, input_file, config):

        match = re.match(r'^(\w{2,3})-\d{2,3}\.\d$', frequency_code)
        
        if match is None:
            raise InvalidFrequency

        self.country = match.group(1)
        self.input_file = input_file
        self.frequency_code = frequency_code
        
        self.output_endpoint = random.choice(config['retransmitter_endpoints'][self.country])['input']
        self.admin_endpoint = random.choice(config['retransmitter_endpoints'][self.country])['admin']

    def _start_connections(self):
        
        self.bitrate, self.data = wavfile.read(self.input_file)

        self.context = zmq.Context()
        self.output_socket = self.context.socket(zmq.PUSH)
        self.output_socket.connect('tcp://{}'.format(self.output_endpoint))

        self.admin_socket = self.context.socket(zmq.REQ)
        self.admin_socket.connect('tcp://{}'.format(self.admin_endpoint))

        self.admin_socket.send_json({"type": "start_transmitting", "frequency": self.frequency_code})
        response = self.admin_socket.recv_json()
        
        return response['status'] == 'ok'

    def _transmit(self):
        
        try:
            data_length = len(self.data)
            window_size = self.bitrate
            
            while True:
                offset = 0
                while data_length > offset + window_size:
                    self.output_socket.send_multipart(\
                        [self.frequency_code.encode(), self.data[offset : offset + window_size]])
                    offset += window_size
                    sleep(0.99)
        except KeyboardInterrupt:
            pass

    def _close(self, disconnect):
        
        self.output_socket.close()
        
        if disconnect:
            self.admin_socket.send_json({"type": "stop_transmitting", "frequency": self.frequency_code})
            if self.admin_socket.recv_json()['status'] != 'ok':
                print('Error')
        
        self.admin_socket.close()
        self.context.term()

    def run(self):
        
        can_transmit = self._start_connections()
        if can_transmit:
            self._transmit()
        self._close(can_transmit)


