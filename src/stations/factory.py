class StationFactory(object):

    def get_station(self, mode, freq, config):

        # Returns different kind of stations
        # depending on 'mode': RX | TX
