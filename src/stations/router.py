import zmq
from multiprocessing import Process
from hashlib import md5
import json

END_TOKEN = 'END'

class Router(Process):
    def __init__(self, node_number, config):
        self.input_endpoint = config['routers_endpoints'][node_number]['input']
        self.output_endpoint = config['routers_endpoints'][node_number]['output']
        self.number_of_threads = int(config['routers_endpoints'][node_number].get('number_of_threads', 1))
        super(Router, self).__init__()

    def _start_connections(self):
        self.context = zmq.Context(self.number_of_threads)
        # Socket facing clients

        self.input_socket = self.context.socket(zmq.PULL)
        self.input_socket.bind('tcp://{}'.format(self.input_endpoint))
    
        # Socket facing services
        self.output_socket = self.context.socket(zmq.PUB)
        self.output_socket.bind("tcp://{}".format(self.output_endpoint))

    def _get_message(self):
        print('listening in  {}'.format(self.input_endpoint))
        return self.input_socket.recv_multipart()
    
    def _forward_message(self, topic, message):
        print ('xxxxxxxxxxxxxxx')
        print (topic)
        print (message)
        print ('xxxxxxxxxxxxxxx')
        self.output_socket.send_multipart([topic, message])

    def run(self):
        try:
            self._start_connections()
            while True:
                topic, message = self._get_message()
                self._forward_message(topic, message)
        except Exception as e:
            print (e)
            print ("bringing down zmq device")
        finally:

            self.input_socket.close()
            self.output_socket.close()
            self.context.term()
