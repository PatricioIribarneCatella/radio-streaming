from multiprocessing import Process
import zmq
from time import sleep
from scipy.io import wavfile


class Sender(Process):

    def __init__(self, frequency_code, config):
        self.input_file = config['input_file']
        self.output_endpoint = config['output_endpoint']
        self.frequency_code = frequency_code

    def _start_connections(self):
        self.bitrate, self.data = wavfile.read(self.input_file)

        self.context = zmq.Context()
        self.output_socket = self.context.socket(zmq.PUB)
        
        self.output_socket.bind('tcp://{}'.format(self.output_endpoint))

    def _transmit(self):
        data_length = len(self.data)
        window_size = self.bitrate
        while True:
            offset = 0
            while data_length > offset + window_size:
                self.output_socket.send_multipart(\
                    [self.frequency_code.encode(), self.data[offset : offset + window_size]])
                offset += window_size
                sleep(0.9)

    def _close(self):
        self.output_socket.close()
        self.context.term()

    def run(self):
        self._start_connections()
        self._transmit()
        self._close()