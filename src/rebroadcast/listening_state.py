from collections import Counter

class ListeningState(object):

    def __init__(self):
        self.listening_freqs = Counter()

    def add(self, freq):
        
        self.listening_freqs.update([freq])
        
        return self.listening_freqs[freq] == 1
    
    def remove(self, freq):
        
        if self.listening_freqs[freq] > 0:
            self.listening_freqs.subtract([freq])
        
        return self.listening_freqs[freq] == 0


