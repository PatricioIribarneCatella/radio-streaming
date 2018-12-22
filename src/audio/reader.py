from scipy.io import wavfile

class AudioReader(object):

    def __init__(self, input_file):
        self.bitrate, self.data = wavfile.read(input_file)
        self.offset = 0

    def chunks(self):
        
        data_length = len(self.data)
        window = self.bitrate

        while data_length > self.offset + window:
            r = self.data[self.offset : self.offset + window]
            self.offset += window
            yield r

    def reset(self):
        self.offset = 0


