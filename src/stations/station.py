import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from factory import StationFactory

class RadialStation(object):

    def __init__(self, type_station, freq, config):

        self.type_station = type_station
        self.freq = freq

        self.station = StationFactory().get_station(type_station, freq, config)

    def run(self):

        print("Station running: {} in {} frequency".format(
                    self.type, self.freq))

        station.start()

