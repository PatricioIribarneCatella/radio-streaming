from scipy.io import wavfile

class AudioReader(object):

    def __init__(self, input_file):

        self.bitrate, self.data = wavfile.read(input_file)
        self.length = len(self.data)
        self.offset = 0

    def chunks(self):

        window = self.bitrate

        while self.offset < self.length:
            if self.offset + window >= self.length:
                chunk = self.data[self.offset :]
                self.offset = self.length
            else:
                chunk = self.data[self.offset : self.offset + window]
                self.offset += window + 1
            yield chunk

    def reset(self):
        self.offset = 0


