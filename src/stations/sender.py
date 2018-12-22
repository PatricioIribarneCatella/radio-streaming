from time import sleep

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from audio.reader import AudioReader
from middleware.managers import SenderStation
from stations.transmitter import Transmitter
from stations.listeners import SenderListener

class Sender(object):

    def __init__(self, frequency_code, country, input_file, config):

        self.country = country
        self.input_file = input_file
        self.frequency_code = frequency_code
        
        self.audio = AudioReader(self.input_file)

        self.output_endpoint = random.choice(config['retransmitter_endpoints'][self.country])['input']
        self.admin_endpoint = random.choice(config['retransmitter_endpoints'][self.country])['admin']

    def _start_connections(self):

        self.connection = SenderStation(self.country,
                                        self.frequency_code,
                                        self.config)

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
            while True:

                for chunk in self.audio.chunks():

                    self.connection.send(chunk)
                    sleep(0.99)

                self.audio.reset()

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


