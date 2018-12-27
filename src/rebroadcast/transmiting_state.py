from datetime import datetime, timedelta

TIMEOUT = 5

class InUseFreq(Exception):
    pass

class TransmitingState(object):

    def __init__(self):
        self.active_freqs = dict()

    def add(self, freq):
        
        if freq in self.active_freqs:
            now = datetime.now()
            if now - self.active_freqs[freq] < timedelta(seconds=TIMEOUT):
                raise InUseFreq()
        
        self.active_freqs[freq] = datetime.now()
   
    def update(self, freq):

        self.active_freqs[freq] = datetime.now()

    def remove(self, freq):
        
        try:
            del self.active_freqs[freq]
        except KeyError:
            pass


