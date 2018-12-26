import sys
from os import path
from time import sleep

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from audio.reader import AudioReader
from middleware.managers import SenderStation
from stations.transmitter import Transmitter
from stations.listeners import SenderListener

class Sender(object):

    def __init__(self, frequency_code, country, input_file, config):

        self.config = config
        self.country = country
        self.input_file = input_file
        self.frequency_code = frequency_code
        
        self.audio = AudioReader(self.input_file)

    def _initialize(self):

        self.connection = SenderStation(self.country,
                                        self.frequency_code,
                                        self.config)

        # Query the antenna leader for
        # permission on transmitting this frequency
        res = self.connection.query()

        return res

    def _transmit(self):
        
        try:
            while True:

                for chunk in self.audio.chunks():

                    self.connection.transmit(chunk)
                    sleep(0.99)

                self.audio.reset()

        except KeyboardInterrupt:
            pass

    def run(self):
        
        can_transmit = self._initialize()
        
        if can_transmit:

            t = Transmitter(self.country,
                            self.frequency_code,
                            self.config)
            t.start()

            l = SenderListener(self.country,
                               self.frequency_code,
                               self.config)
            l.start()

            self._transmit()

        self.connection.close()


