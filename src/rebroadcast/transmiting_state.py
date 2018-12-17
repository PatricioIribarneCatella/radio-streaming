class InUseFreq(Exception):
    pass

class TransmitingState(object):

    def __init__(self):
        self.active_freqs = dict()

    def add(self, freq, transmiter_id):
        if freq in self.active_freqs:
            raise InUseFreq()
        self.active_freqs[freq] = transmiter_id
    
    def remove(self, freq):
        try:
            del self.active_freqs[freq]
        except KeyError:
            pass