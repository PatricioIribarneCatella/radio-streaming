import zmq
from multiprocessing import Process

class Listener(Process):
    def __init__(self, config):
        self.routers_endpoints = config['routers_endpoints']
        self.number_of_threads = config.get('number_of_threads', 1)
        super(Listener, self).__init__()

    def _start_connections(self):
        self.context = zmq.Context(self.number_of_threads)
        self.poller = zmq.Poller()

        # Socket facing routers
        self.input_sockets = []
        for router in self.routers_endpoints:
            input_socket = self.context.socket(zmq.SUB)
            input_socket.connect('tcp://{}'.format(router))
            self.poller.register(input_socket, zmq.POLLIN)
            self.input_sockets.append(input_socket)
    
    def _get_new_subscriptions(self):
        return ['']

    def _subscribe(self, topic):
        for socket in self.input_sockets:
            socket.setsockopt_string(zmq.SUBSCRIBE, str(topic))
        
    def _get_current_messages(self):
        for socket_with_data in dict(self.poller.poll(100)):
            topic, message = socket_with_data.recv_multipart()
            print(topic, message)
            yield topic, message

    def _forward_message(self, topic, message):
        print('-----')
        print(topic)
        print(message)
        print('-----')
        
    def _close():
        for socket in self.input_sockets:
            socket.close()
        self.context.term()


    def run(self):
        self._start_connections()
        
        while True:
            for topic in self._get_new_subscriptions():
                self._subscribe(topic)
            for topic, message in self._get_current_messages():
                self._forward_message(topic, message)
        
        self._close()



