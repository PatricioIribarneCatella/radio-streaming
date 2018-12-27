import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from audio.player import AudioPlayer
from middleware.managers import ReceiverStation, InternationalReceiverStation
from stations.receptor import Receptor
from stations.listeners import ReceiverListener

class Receiver(object):

    def __init__(self, country, frequency_code, config):
       
        self.config = config
        self.country = country
        self.frequency_code = frequency_code
        
        self.player = AudioPlayer(config.get('bitrate', 16000))

    def _initialize(self):

        self.connection = ReceiverStation(self.frequency_code,
                                          self.country,
                                          self.config)

    def _receive(self):

        try:

            while True:
                for chunk in self.connection.recv():
                    self.player.play(chunk)
        
        except KeyboardInterrupt:
            pass

    def _close(self):
        
        self.connection.close()
        self.player.close()

    def run(self):
        
        self._initialize()

        self._receive()

        self._close()


class InternationalReceiver(object):

    def __init__(self, country, frequency, freq_country, config):

        self.country = country
        self.frequency = frequency
        self.freq_country = freq_country
        self.config = config

        self.player = AudioPlayer(config.get('bitrate', 16000))

    def _initialize(self):
        
        self.connection = InternationalReceiverStation(self.country,
                                                    self.frequency,
                                                    self.config)

    def _receive(self):

        try:

            while True:
                chunk = self.connection.recv()
                self.player.play(chunk)
        except KeyboardInterrupt:
            pass

    def _close(self):

        self.connection.close()
        self.player.close()

    def run(self):

        self._initialize()
        
        r = Receptor(self.country,
                     self.frequency,
                     self.config)

        r.start()

        l = ReceiverListener(self.country,
                             self.frequency,
                             self.config)
        l.start()

        self._receive()
        
        r.join()
        l.join()

        self._close()

