from multiprocessing import Process
import zmq
from time import sleep

class Retransmitter(Process):

    def __init__(self, country, node_number, config):
        self.country = country
        self.node_number = node_number
        self.input_endpoint = config['retransmitter_endpoints'][country][node_number]['input']
        self.output_endpoint = config['retransmitter_endpoints'][country][node_number]['output']
        

    def _start_connections(self):
        self.context = zmq.Context()

        self.input_socket = self.context.socket(zmq.PULL)
        self.input_socket.bind('tcp://{}'.format(self.input_endpoint))

        self.output_socket = self.context.socket(zmq.PUB)
        self.output_socket.bind('tcp://{}'.format(self.output_endpoint))

    def _recv_message(self):
        return self.input_socket.recv_multipart()    

    def _transmit_message(self, frequency, message):
        self.output_socket.send_multipart([frequency, message])

    def _retransmit(self):
        while True:
            frequency, message = self._recv_message()
            self._transmit_message(frequency, message)
            
    def _close(self):
        self.output_socket.close()
        self.input_socket.close()
        self.context.term()

    def run(self):
        self._start_connections()
        self._retransmit()
        self._close()