from collections import Counter
from datetime import datetime, timedelta

TIMEOUT = 5

class InUseFreq(Exception):
    pass

class TransmissionRegistry(object):

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

class InternationalRegistry(object):

    def __init__(self):
        self.listening_freqs = Counter()

    def add(self, freq):
        
        self.listening_freqs.update([freq])
        
        return self.listening_freqs[freq] == 1
    
    def remove(self, freq):
        
        if self.listening_freqs[freq] > 0:
            self.listening_freqs.subtract([freq])
        
        return self.listening_freqs[freq] == 0


