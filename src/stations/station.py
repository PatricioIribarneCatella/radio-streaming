class RadialStation(object):

    def __init__(self, type_station, freq):

        self.type = type_station
        self.freq = freq

    def run(self):

        print("Station running: {} in {} frequency".format(
                    self.type, self.freq))


